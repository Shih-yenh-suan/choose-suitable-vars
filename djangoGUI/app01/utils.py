import itertools
import pandas as pd


def get_stars(p_values, t_values):
    p_values = round(p_values, 3)
    t_values = round(t_values, 3)
    if p_values < 0.01:
        stars = "***"
    elif p_values < 0.05:
        stars = "**"
    elif p_values < 0.1:
        stars = "*"
    else:
        stars = ""
    return (f'{t_values}{stars}', )


def unpack_Braces(input_str):
    """在无嵌套的情况下进行处理。
    如果输入字符串中包含大括号嵌套中括号的情况，
    则结果会返回出嵌套的中括号
    这种情况下还需要处理
    即：本函数保证结果中不含大括号
    """
    # 解析输入，将字符串分成必须包含的部分、选择性包含的部分和普通元素
    required = []
    optional = []
    normal = []

    # 分离大括号和中括号内容
    # 将左大括号变成右大括号，然后按照右大括号分开，此时
    # 由于原左大括号的左边和右边分别代表了大括号外部和内部，而
    # 原右大括号的左边和右边分别代表了大括号内部和外部，因此，
    # 分列之后，就是外部、内部、外部、内部……排列
    # 因此，可以用其序号判断内外部。奇数序号就是内部。
    tokens = input_str.replace('{', '}').split('}')
    for i in range(len(tokens)):
        part = tokens[i].strip()
        if i % 2 == 1:  # 大括号内部，填入对应列表
            required.extend(part.split())
        else:  # 大括号外部，继续执行中括号的内容，也同理
            if '[' in part:  # 存在中括号，处理选择性包含的元素
                optional_part = part.replace('[', ']').split(']')
                for j in range(len(optional_part)):
                    subpart = optional_part[j].strip()
                    if j % 2 == 1:  # 中括号内部，填入 optional
                        optional.append(subpart.split())
                    else:  # 中括号外部
                        if subpart:
                            normal.extend(subpart.split())
            else:  # 不存在中括号的话，填入 normal
                if part:
                    normal.extend(part.split())
    # 生成所有可能的子字符串
    result = []

    # 为选择性包含的元素生成所有组合
    # 对于每个中括号组合，只选择一个或不选
    optional_combinations = []
    for group in optional:
        optional_combinations.append(group + [None])  # 添加None表示该组一个都不选
    # 生成所有中括号组合的笛卡尔积
    all_optional_combinations = list(itertools.product(*optional_combinations))

    # 为普通元素生成所有可能的组合（包括全不选的情况）
    all_normal_combinations = []
    for i in range(len(normal) + 1):
        all_normal_combinations.extend(itertools.combinations(normal, i))

    # 生成所有有效子字符串
    for optionals in all_optional_combinations:
        for normals in all_normal_combinations:
            subset = list(required)  # 开始时包含所有必须包含的元素
            subset.extend(filter(None, optionals))  # 添加选择性元素，过滤掉None
            subset.extend(normals)  # 添加普通元素
            result.append(" ".join(subset))

    return result


def unpack_Bracket(input_str):
    """单独处理包含中括号的情况
    在前面一个函数后，对生成的子字符串列表进行处理
    这些子字符串中仅可能包含中括号，且未被括号包裹的内容必须出现
    因此，与前面的代码相比，删除了 normals 列表
    optional_combinations 中也不需要增加 None，因为中括号中的元素不可以为空
    """
    optional = []
    required = []
    tokens = input_str.replace('[', ']').split(']')
    for j in range(len(tokens)):
        subpart = tokens[j].strip()
        if j % 2 == 1:  # 中括号内部，填入 optional
            optional.append(subpart.split())
        else:  # 中括号外部
            if subpart:
                required.extend(subpart.split())
    # 生成所有可能的子字符串
    result = []

    # 为选择性包含的元素生成所有组合
    # 对于每个中括号组合，只选择一个或不选
    optional_combinations = []
    for group in optional:
        optional_combinations.append(group)  # 添加None表示该组一个都不选
    # 生成所有中括号组合的笛卡尔积
    all_optional_combinations = list(itertools.product(*optional_combinations))

    # 生成所有有效子字符串
    for optionals in all_optional_combinations:
        subset = list(required)  # 开始时包含所有必须包含的元素
        subset.extend(filter(None, optionals))  # 添加选择性元素，过滤掉None
        result.append(" ".join(subset))

    return result


def get_control_variables(input_str, max_num=15, min_num=6):
    """获取控制变量"""
    result_list = unpack_Braces(input_str)
    list = []
    for r in result_list:
        list.extend(unpack_Bracket(r))
    for l in list:
        if len(l.split(' ')) > max_num or len(l.split(' ')) < min_num:
            list.remove(l)
    return list


def change_to_df(cv_list, tuple_list):
    data_dict = {}
    # 将元组列表转换为字典
    for item in tuple_list:
        column_name, value = item
        data_dict[column_name] = [value]
    index_name = cv_list
    df = pd.DataFrame(data_dict, index=[index_name])
    return df


if __name__ == "__main__":
    input_str = r"{Subsidiary_log} Age Dual Big4 Indie Top_Salary_log CR_1 EnvPerformance_log FDI HHI_A {GDP_growth} Prolist MNE [SeperationM SeperationR] {Size ROA Growth Lev } Cur PPE Invint"
    print(len(get_control_variables(input_str)))
