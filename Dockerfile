FROM python
COPY chatbot.py / \
     picture / \
     requirements.txt /

RUN pip install update \
    && pip install -r requirements.txt 

ENV ACCESS_TOKEN 5211434946:AAEv-3PvEJ98N1ufat_t96KDgUyyuzl3KZY
ENV HOST comp7940.cfwyvlywfwy6.us-east-1.rds.amazonaws.com
ENV USER admin
ENV PASSWORD 12345678
ENV DB comp7940

ENTRYPOINT ["python","chatbot.py"]
