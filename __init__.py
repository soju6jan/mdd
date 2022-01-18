import os, sys
try:
    import plotly
except:
    os.system("pip install plotly")

try:
    import yfinance
except:
    os.system("pip install yfinance")

try:
    import pandas
except:
    os.system("pip install pandas")

try:
    import pandas_datareader
except:
    os.system("pip install pandas-datareader")

from flask import render_template, redirect
from .core import mdd
from plugin import LogicModuleBase
from mod import P, package_name, logger
name = 'mdd'


class MDD(LogicModuleBase):
    def __init__(self, PP):
        super(MDD, self).__init__(P, 'index')
        self.name = name
        
    def process_menu(self, sub, req):
        graph_json = mdd(sub)
        return render_template(f"{package_name}_{name}_index.html", graph_json=graph_json)
 

mod_info = {
    'mod_class' : MDD,
    'sub' : ['mdd', 'MDD'],
    'sub2' : [['SPY', 'SPY'], ['TSLA', '테슬라'], ['AAPL', '애플']],
    'version' : '1.0.0',
}