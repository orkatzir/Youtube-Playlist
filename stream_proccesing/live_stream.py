from youtube_watcher import main
from prefect import flow,task

@flow(name="Stream live")
def live_stream_run():
    main()
    

if __name__ == '__main__':
  live_stream_run()