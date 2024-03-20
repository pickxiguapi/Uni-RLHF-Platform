import datetime


def to_dict(model_instance):
    return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

def datetime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

ALLOWED_EXTENSIONS = {'hdf5', 'h5'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS