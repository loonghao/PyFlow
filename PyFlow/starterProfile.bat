%cd%/Python27/Scripts/python.exe -m cProfile -o program.prof "%cd%/PyFlow.py"
%cd%/Python27/Scripts/snakeviz.exe program.prof
pause