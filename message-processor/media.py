from lib.queue import q

def new_file_present(json_string):
    q.enqueue('audio.new_file_present', json_string)
