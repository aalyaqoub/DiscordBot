FROM ubuntu:20.04 as base

RUN apt update
RUN apt upgrade -y
RUN apt install software-properties-common -y
RUN apt install python3-pip -y
RUN apt install ffmpeg -y
RUN apt install nano -y
RUN apt install tmux -y

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        alsa-base \
        alsa-utils \
        libsndfile1-dev && \
    apt-get clean

RUN pip install openai
RUN pip install discord.py
RUN pip install "discord.py[voice]"
# RUN pip install youtube_dl==2021.12.17 # youtube_dl has not been updated in a while so it doesn't work well
RUN pip install yt-dlp

ENTRYPOINT ["python3 ./bot/bot.py"]
