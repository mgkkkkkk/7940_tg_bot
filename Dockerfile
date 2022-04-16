FROM python
COPY chatbot.py / \
     picture / \
     requirements.txt /

RUN pip install update \
    && pip install -r requirements.txt 

ENV ACCESS_TOKEN 5211434946:AAEv-3PvEJ98N1ufat_t96KDgUyyuzl3KZY
ENV HOST 192.168.95.100
ENV USER root
ENV PASSWORD 123456
ENV DB comp7940

ENTRYPOINT ["python","chatbot.py"]
