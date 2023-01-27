def format_filename(id,filename):
    ext = filename.rsplit('.', 1)[1].lower()
    new_name = str(id) + '.' + ext
    return new_name