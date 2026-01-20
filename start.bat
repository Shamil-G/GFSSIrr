# python -m venv venv

call C:\Projects\GFSSIrr\venv\Scripts\activate.bat
rem . /home/pens/GFSSIrr/venv/bin/activate

python -m pip install --upgrade pip
pip install --upgrade pip
#pip install ldap3

rem gunicorn
rem #python main_app.py
rem #gunicorn -w 2 -b 0.0.0.0:5081 main_app:app
rem #gunicorn -w 2 --preload main_app:app
rem #gunicorn -w 2 -k sync main_app:app
rem python -m pip install --upgrade pip
rem pip install --upgrade pip
rem pip3 install celery
python main_app.py
