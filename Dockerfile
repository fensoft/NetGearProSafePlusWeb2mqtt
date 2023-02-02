FROM python:3.7-alpine
WORKDIR /config
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY netgear.py .
COPY boot.sh /boot
RUN chmod a+x /boot /config/netgear.py
ENV SWITCH_IP=
ENV SWITCH_PASSWORD=
ENV MQTT_IP=
ENV MQTT_TOPIC=switch
ENV DELAY_STATS=15
ENV DELAY_CONFIG=120
CMD [ "/boot" ]
