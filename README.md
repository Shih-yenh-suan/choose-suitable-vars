# 使用方法

## 安装依赖

```
pip install pandas
pip install statsmodels
pip install linearmodels
```

## 新建 config.py 并修改参数

```python
Varlist = {
    'dv': '', # 此处填入自变量
    'iv': '', # 此处填入因变量
    'cv': '', # 此处填入控制变量
    'fe': '', # 此处填入固定效应
    'mod': '', # 此处填入调节变量
    'symbol': '', # 此处填入公司代码
    'date': '' # 此处填入日期
}
path = ""
```

Varlist：

1. 格式要求：
   自变量、因变量、公司代码、日期：必须只能填入一个字符。
   控制变量、固定效应、调节变量可以填入多个变量，每个变量以空格隔开，就像 stata 里做的一样
   日期：必须是日期而非年份。在 stata 中也为日期格式

2. 控制变量：可以用大括号括起来必须包含的控制变量，用中括号括起来只能包含一个的变量。例如：`{Size SOE} Age [ROA ROAB] GDP`，意味着 控制变量必须包含 Size 和 SOE，ROA 和 ROAB 只能包含一个。

path: 指定 stata 的.dta 文件的保存路径。

## 在 main.py 中选择模型

将第 161 行替换为：

```python
# 公司固定效应模型：
result_list = model_regresser.xtreg_model()

# 混合OLS模型，控制聚类稳健标准误
result_list = model_regresser.reg_model("r")

# 混合OLS模型，公司聚类
result_list = model_regresser.reg_model("Symbol")
```

## 运行 main.py

## Todo

1. 在结果中汇报带星号的系数和 t 值
