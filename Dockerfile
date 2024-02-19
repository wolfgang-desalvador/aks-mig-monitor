FROM debian:stable-slim

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install python3-venv -y
RUN mkdir -p /opt/
RUN mkdir -p /opt/scripts
RUN python3 -m venv /opt/mig-monitor
RUN /opt/mig-monitor/bin/pip3 install kubernetes
COPY mig_monitor.py /opt/
ENV PYTHONUNBUFFERED=1
CMD ["/opt/mig-monitor/bin/python3","/opt/scripts/mig_monitor.py"]