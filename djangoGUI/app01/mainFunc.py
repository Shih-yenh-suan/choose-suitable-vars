"""
输入：

dta表格路径
指定自变量、因变量、调节变量（可选）、必须包含的控制变量、待选择控制变量列表：用dict形式输入
指定因变量和调节变量的显著度下限
指定回归模型：先做个xtreg-fe/reg/reg-r/reg-vceSymbol


输出：

应选择的控制变量（给出全部最小结果）

封装成页面

"""
from tqdm import tqdm
import os
import warnings
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels import PanelOLS
from linearmodels.panel.model import AbsorbingEffectWarning
from config import *
from utils import *


class ModelChoosing:
    def __init__(self, df, dict, cv_string):
        self.dict = dict
        self.iv = df[dict["iv"]]
        self.dv = df[dict["dv"]]
        self.cv = df[cv_string.split()]
        self.cv_string = cv_string
        self.fe = df[dict["fe"].split()]
        self.mod = df[dict["mod"].split()] if 'mod' in dict else None
        self.symbol = df[dict["symbol"]]
        self.date = df[dict["date"]]

    def optionAndGroups(self, option, data):
        if option == None:
            cov_type = "nonrobust"
            cov_kwds = None
        elif option == "r":
            cov_type = "HC1"
            cov_kwds = None
        elif option == "Symbol":
            cov_type = "cluster"
            cov_kwds = {'groups': data[self.dict["symbol"]]}
        return cov_type, cov_kwds

    def reg_model(self, options=None):
        '''返回混合OLS的回归结果'''
        # 存储所有结果
        data_dict = {}
        # 合并数据
        data = pd.concat([self.iv, self.dv, self.cv, self.fe,
                          self.symbol, self.date], axis=1)
        for col in self.mod.columns:
            moderator = self.mod[[col]]
            data = pd.concat([data, moderator], axis=1)
        available_data = data.loc[:, data.columns].dropna(how='any')
        # 生成回归指令
        cv_formula = ' + '.join(self.cv.columns)
        fe_formula = ' + '.join(f'C({col})' for col in self.fe.columns)
        formula_basic = f'{self.dict["dv"]} ~ {self.dict["iv"]} + {cv_formula} + {fe_formula}'

        print(formula_basic)
        # 生成模型
        model = smf.ols(formula_basic, data=available_data, missing="drop")
        # 根据 option 生成聚类方法
        cov_type, cov_kwds = self.optionAndGroups(options, available_data)
        result = model.fit(cov_type=cov_type, cov_kwds=cov_kwds)
        p_values = result.pvalues[self.dict["iv"]]
        t_values = result.tvalues[self.dict["iv"]]
        data_dict["main"] = [*get_stars(p_values, t_values)]

        if self.mod is not None:
            for col in self.mod.columns:
                mod_formula = f'{col} + {col}:{self.dict["iv"]}'
                formula = f'{formula_basic} + {mod_formula}'
                model = smf.ols(formula, data=available_data)
                cov_type, cov_kwds = self.optionAndGroups(
                    options, available_data)
                result = model.fit(cov_type=cov_type, cov_kwds=cov_kwds)
                p_values = result.pvalues[f'{col}:{self.dict["iv"]}']
                t_values = result.tvalues[self.dict["iv"]]
                data_dict[f"mod:{col}"] = [*get_stars(p_values, t_values)]

        index_name = self.cv_string
        df = pd.DataFrame(data_dict, index=[index_name])
        return df

    def xtreg_model(self):
        '''返回固定效应模型的回归结果'''
        # 存储所有结果
        data_dict = {}
        data = pd.concat([self.iv, self.dv, self.cv,
                         self.symbol, self.date, self.fe], axis=1)
        data.set_index([self.dict["symbol"], self.dict["date"]], inplace=True)
        # 构建模型公式
        cv_formula = ' + '.join(self.cv.columns)
        fe_formula = ' + '.join(f'C({col})' for col in self.fe.columns)
        formula_basic = f'{self.dict["dv"]} ~ {self.dict["iv"]} + {cv_formula} + {fe_formula} + EntityEffects + TimeEffects'
        # 使用 PanelOLS 进行固定效应模型拟合
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=AbsorbingEffectWarning)
            model = PanelOLS.from_formula(
                formula_basic, data, drop_absorbed=True)
            result = model.fit()
        # 提取结果
        p_values = result.pvalues[self.dict["iv"]]
        t_values = result.tstats[self.dict["iv"]]
        data_dict["main"] = [*get_stars(p_values, t_values)]
        # return result.summary
        if self.mod is not None:
            for col in self.mod.columns:
                moderator = self.mod[[col]]
                data = pd.concat([self.iv, self.dv, self.cv, self.fe,
                                  self.symbol, self.date, moderator], axis=1)
                data.set_index(
                    [self.dict["symbol"], self.dict["date"]], inplace=True)
                mod_formula = f'{col} + {col}:{self.dict["iv"]}'
                formula = f'{self.dict["dv"]} ~ {self.dict["iv"]} + {cv_formula} + {fe_formula} + {mod_formula} + EntityEffects + TimeEffects'
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore", category=AbsorbingEffectWarning)
                    model = PanelOLS.from_formula(
                        formula, data, drop_absorbed=True)
                    result = model.fit()
                p_values = result.pvalues[f'{col}:{self.dict["iv"]}']
                t_values = result.tstats[self.dict["iv"]]
                data_dict[f"mod:{col}"] = [*get_stars(p_values, t_values)]
        index_name = self.cv_string
        df = pd.DataFrame(data_dict, index=[index_name])
        return df

    def get_suitable_cv(self, model_choosen):
        result_tuple_list = model_choosen()
        for result in result_tuple_list:
            if result[0] == "main":
                p_value = result[1][0]
                if p_value > 0.1:
                    print(f"{self.cv_name} 主效应不通过")
                    return False
                else:
                    print(f"{self.cv_name} 主效应通过，{result[1][1]}")
            if result[0][:3] == "mod":
                p_value = result[1][0]
                if p_value > 0.1:
                    print(f"{self.cv_name} 调节效应不通过")
                else:
                    print(f"{self.cv_name} 调节效应通过，{result[1][1]}")


if __name__ == "__main__":
    df = pd.read_stata(path)
    cv_list = get_control_variables(Varlist['cv'])
    # 保存到文件中。
    # 明确是否保存时增加header：
    # 如果文件不存在，则header为True；如果文件存在，说明已经给过了。
    if not os.path.exists('results.csv'):
        header = True
    else:
        header = False
    result_df = pd.DataFrame()
    for cv in tqdm(cv_list):
        print(f"当前控制变量：{cv}")
        model_regresser = ModelChoosing(df, Varlist, cv)
        result_list = model_regresser.reg_model("Symbol")
        result_list.to_csv(r'choose-suitable-vars\results.csv',
                           mode='a', header=header)
        result_df = pd.concat([result_df, result_list], axis=0)
        # 第一次保存，由于文件不存在，写入 header
        # 后续将 header 改为 false ，防止再写入
        header = False
        # change_to_df(cvs, result_list)
    print(result_df)
