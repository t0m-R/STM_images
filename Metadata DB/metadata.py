import hashlib
import logger
import os


def get_img_hash(img):
    img_hash = hashlib.md5()
    with open(img, 'rb') as f:
        data = f.read()
        img_hash.update(data)
    return img_hash.hexdigest()


def get_hardcoded_metadata(path):
    # get metadata hardcoded in path
    year = path.split('/')[4]
    tmp = path.split('/')[5]
    if tmp[:4] != year or path.split('/')[6] == 'FASTSTM':
        meta = dict()
        fwd = path[:-3] + 'tf0'
        bwd = path[:-3] + 'tb0'
        meta['ImageOriginalName'] = os.path.join(path)
        try:
            meta['ImageHashName'] = str(get_img_hash(fwd))
        except FileNotFoundError:
            logging.error('TF0 not found for {}'.format(img))
            try:
                meta['ImageHashName'] = str(get_img_hash(bwd))
            except FileNotFoundError:
                logging.error('TB0 not found for {}'.format(img))
                return None
        return meta
    return None


def load_par(path):
    with open(path) as f:
        meta = f.readlines()
    if not meta:
        logging.info('Empty par file for {}'.format(path))
        return None
    meta = [x.strip('\n') for x in meta]
    return meta


def get_comment(meta):
    start, end = 0, 0
    for j, line in enumerate(meta):
        if line.startswith('Comment'):
            start = j
        if line.startswith('; Scanner Description'):
            end = j
    try:
        comment = ''.join(meta[start:end])
        escape = ['?', '*', '"', '.']
        for j in escape:
            comment = comment.replace(j, '')
        comment = comment.replace("'", "")
    except:
        logging.info('Comment parsing error for {}'.format(path))
        comment = 'Comment:'
    if start != 0:
        for i in range(start, end + 1):
            del meta[start]
        meta.insert(start, comment)
    return meta


def clean_strings(meta):
    # Remove newline character and whitespaces
    meta = [e.strip('\n') for e in meta]
    meta = [e.replace(' ', '') for e in meta]
    # Remove final comment part
    meta = [e.split(';', 1)[0] for e in meta]
    # Remove empty lines
    meta = [e for e in meta if e not in ('', ';')]
    return meta


def get_metadata_dict(meta):
    # Add key to channel parameters, for each channel
    ch_list = list()
    img_list = list()
    spec_list = list()
    spec_parameter = ''
    for i, line in enumerate(meta):
        if 'TopographicChannel' in line:
            ch_name = meta[i + 8][-3:].upper() + "_"
            meta[i] = ch_name + meta[i]
            meta[i + 1] = ch_name + 'Direction:' + meta[i + 1]
            meta[i + 2] = ch_name + 'MinimumRawValue:' + meta[i + 2]
            meta[i + 3] = ch_name + 'MaximumRawValue:' + meta[i + 3]
            meta[i + 4] = ch_name + 'MinimumPhysValue:' + meta[i + 4]
            meta[i + 5] = ch_name + 'MaximumPhysValue:' + meta[i + 5]
            meta[i + 6] = ch_name + 'Resolution:' + meta[i + 6]
            meta[i + 7] = ch_name + 'PhysicalUnit:' + meta[i + 7]
            meta[i + 8] = ch_name + 'Filename:' + meta[i + 8]
            meta[i + 9] = ch_name + 'DisplayName:' + meta[i + 9]
            ch_list.append(ch_name)
            img_list.append(ch_name)
        elif 'SpectroscopyChannel' in line:
            ch_name = meta[i + 16][-3:].upper() + "_"
            meta[i] = ch_name + meta[i]
            spec_parameter = meta[i + 1]
            meta[i + 1] = ch_name + 'Parameter:' + meta[i + 1]
            meta[i + 2] = ch_name + 'Direction:' + meta[i + 2]
            meta[i + 3] = ch_name + 'MinimumRawValue:' + meta[i + 3]
            meta[i + 4] = ch_name + 'MaximumRawValue:' + meta[i + 4]
            meta[i + 5] = ch_name + 'MinimumPhysValue:' + meta[i + 5]
            meta[i + 6] = ch_name + 'MaximumPhysValue:' + meta[i + 6]
            meta[i + 7] = ch_name + 'Resolution:' + meta[i + 7]
            meta[i + 8] = ch_name + 'PhysicalUnit:' + meta[i + 8]
            meta[i + 9] = ch_name + 'NumberSpecPoints:' + meta[i + 9]
            meta[i + 10] = ch_name + 'StartPoint:' + meta[i + 10]
            meta[i + 11] = ch_name + 'EndPoint:' + meta[i + 11]
            meta[i + 12] = ch_name + 'Increment:' + meta[i + 12]
            meta[i + 13] = ch_name + 'AcqTimePerPoint:' + meta[i + 13]
            meta[i + 14] = ch_name + 'DelayTimePerPoint:' + meta[i + 14]
            meta[i + 15] = ch_name + 'Feedback:' + meta[i + 15]
            meta[i + 16] = ch_name + 'Filename:' + meta[i + 16]
            meta[i + 17] = ch_name + 'DisplayName:' + meta[i + 17]
            ch_list.append(ch_name)
            spec_list.append(ch_name)
        elif spec_parameter + 'Parameter' in line:
            meta[i] = 'SpecParam:' + spec_parameter
            meta[i + 1] = 'SpecParamRampSpeedEnabled:' + meta[i + 1]
            meta[i + 2] = 'SpecParamT1us:' + meta[i + 2]
            meta[i + 3] = 'SpecParamT2us:' + meta[i + 3]
            meta[i + 4] = 'SpecParamT3us:' + meta[i + 4]
            meta[i + 5] = 'SpecParamT4us:' + meta[i + 5]

    # Split list into pairs
    meta = [entry.split(':', 1) for entry in meta]
    for entry in meta:
        if len(entry) == 1:
            entry.insert(1, '')

    # Create dictionary for metadata
    try:
        meta = {k: v for k, v in meta}
    except:
        logging.error('Metadata extraction error for {}'.format(path))
        meta = dict()

    return meta


def fix_timestamp(meta):
    # Adjust date as YYYY-MM-DD and time as HH:MM
    try:
        year = '20' + meta['Date'][6:8]
        month = meta['Date'][3:5]
        day = meta['Date'][0:2]
        hours = meta['Date'][8:10]
        seconds = meta['Date'][11:13]
        meta['Time'] = hours + ':' + seconds
        meta['Date'] = year + '-' + month + '-' + day
        # Calculate timestamp in seconds
        time_stamp = meta['Date'] + 'T' + meta['Time'] + ":00"
        meta['Timestamp'] = time_stamp
    except:
        logging.info('Date parsing error for {}'.format(path))
    return meta


def get_par_metadata(path):
    meta = load_par(path)
    if meta is not None:
        meta = get_comment(meta)
        meta = clean_strings(meta)
        meta = get_metadata_dict(meta)
        meta = fix_timestamp(meta)
    return meta


def get_date(path):
    tmp = path.split('/')[5]
    date = path[:4] + '-' + tmp[4:6] + '-' + tmp[6:]
    return date
