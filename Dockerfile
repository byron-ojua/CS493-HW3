FROM python:3.12
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .
ENV PORT=8080
EXPOSE ${PORT}
CMD [ "./run.sh" ]