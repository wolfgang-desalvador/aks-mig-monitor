FROM debian:stable-slim

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install python3-venv -y
RUN mkdir -p /opt/
RUN mkdir -p /opt/scripts
RUN python3 -m venv /opt/aks-mig-monitor
RUN /opt/aks-mig-monitor/bin/pip3 install kubernetes
COPY mig_monitor.py /opt/scripts/
ENV PYTHONUNBUFFERED=1
CMD ["/opt/aks-mig-monitor/bin/python3","/opt/scripts/mig_monitor.py"]