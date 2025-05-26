FROM continuumio/miniconda3

WORKDIR /app

ENV PATH /opt/conda/bin:$PATH
RUN apt-get update && apt-get install -yq curl wget jq vim

COPY environment.yml /app/environment.yml
RUN conda env create -f /app/environment.yml

SHELL ["conda", "run","-n", "python_env", "/bin/bash", "-c"]
#SHELL ["conda", "run", "--no-capture-output","-n", "python_env", "/bin/bash", "-c"]

RUN pip install --no-cache-dir git+https://github.com/bp-kelley/descriptastorus "flaml[automl]"



#RUN rm /bin/sh && ln -s /bin/bash /bin/sh

COPY . /app
ENV PYTHONUNBUFFERED=1

EXPOSE 9999

CMD [ "/bin/bash", "-c", "source activate python_env && nohup jupyter lab --ip=0.0.0.0 --port=8080 --no-browser --allow-root --NotebookApp.token='' > jupyter.log 2>&1 & bash" ]
#CMD [ "/bin/bash", "-c", "source activate python_env" ]

# The code to run when container is started: 
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "python_env", "python", "app.py"]
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "python_env"]
