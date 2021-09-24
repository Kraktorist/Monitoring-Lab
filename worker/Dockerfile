FROM python
COPY ./requirements.txt .
COPY ./*.py .
RUN pip install -r requirements.txt

CMD python -u app.py