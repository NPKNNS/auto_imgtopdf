import time

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar_length = 50
    filled_length = int(bar_length * progress // total)
    empty_length = bar_length - filled_length
    bar = '█' * filled_length + '-' * empty_length
    print(f"\r|{bar}| {percent:.2f}%", end="")