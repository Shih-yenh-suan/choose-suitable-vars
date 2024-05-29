import os
import pandas as pd
from .forms import VarlistForm
from django.shortcuts import render, HttpResponse
from .mainFunc import ModelChoosing, get_control_variables
# Create your views here.
from django.conf import settings


def index(request):
    return HttpResponse("Hello World")


def run_code(request):
    if request.method == 'POST':
        form = VarlistForm(request.POST, request.FILES)
        if form.is_valid():
            # 处理用户提交的数据
            dv = form.cleaned_data['dv']
            iv = form.cleaned_data['iv']
            cv = form.cleaned_data['cv']
            fe = form.cleaned_data['fe']
            mod = form.cleaned_data['mod']
            symbol = form.cleaned_data['symbol']
            date = form.cleaned_data['date']
            dta_file = form.cleaned_data['dta_file']
            Varlist = {
                "dv": dv,
                "iv": iv,
                "cv": cv,
                "fe": fe,
                "mod": mod,
                "symbol": symbol,
                "date": date,
            }
            # 保存上传的dta文件
            file_path = os.path.join(settings.MEDIA_ROOT, dta_file.name)
            with open(file_path, 'wb') as file:
                for chunk in dta_file.chunks():
                    file.write(chunk)

            # 读取上传的dta文件
            df = pd.read_stata(file_path)

            # 执行你的代码
            cv_list = get_control_variables(cv)
            result_df = pd.DataFrame()

            for cv in cv_list:
                print(f"当前控制变量：{cv}")
                model_regresser = ModelChoosing(df, Varlist, cv)
                result_list = model_regresser.reg_model("r")
                result_list.to_csv('results.csv', mode='a',
                                   header=not os.path.exists('results.csv'))
                result_df = pd.concat([result_df, result_list], axis=0)

            print(result_df)

    else:
        form = VarlistForm()

    return render(request, 'main.html', {'form': form})
