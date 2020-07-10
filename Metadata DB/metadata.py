import hashlib
import logger
import os

def ImageHash(imm):
    hash = hashlib.md5()
    with open(imm, 'rb') as img:
        buf = img.read()
        hash.update(buf)
    return hash.hexdigest()


def loadParMeta(path):
    meta = loadPar(path)
    if meta is not None:
	meta = addComment(meta)
	meta = cleanStrings(meta)
	meta = createDict(meta)
	meta = fixTimestamp(meta)
    return meta


def cleanStrings(meta):
    # Remove newline character and whitespaces
    meta = [e.strip('\n') for e in meta]
    meta = [e.replace(' ','') for e in meta]
    # Remove final comment part
    meta = [e.split(';',1)[0] for e in meta]
    # Remove empty lines
    meta = [e for e in meta if e not in ('', ';')]
    return meta


def createDict(meta):
    # Add key to channel parameters, for each channel
    chlist = list()
    imglist = list()
    speclist = list()
    SpecParameter = ''
    for i,e in enumerate(meta):
        if 'TopographicChannel' in e:
            chName = meta[i+8][-3:].upper()+"_"
            meta[i] = chName+meta[i]
            meta[i+1] = chName+'Direction:'+meta[i+1]
            meta[i+2] = chName+'MinimumRawValue:'+meta[i+2]
            meta[i+3] = chName+'MaximumRawValue:'+meta[i+3]
            meta[i+4] = chName+'MinimumPhysValue:'+meta[i+4]
            meta[i+5] = chName+'MaximumPhysValue:'+meta[i+5]
            meta[i+6] = chName+'Resolution:'+meta[i+6]
            meta[i+7] = chName+'PhysicalUnit:'+meta[i+7]
            meta[i+8] = chName+'Filename:'+meta[i+8]
            meta[i+9] = chName+'DisplayName:'+meta[i+9]
            chlist.append(chName)
            imglist.append(chName)
        elif 'SpectroscopyChannel' in e:
            chName = meta[i+16][-3:].upper()+"_"
            meta[i] = chName+meta[i]
            SpecParameter = meta[i+1]
            meta[i+1] = chName+'Parameter:'+meta[i+1]
            meta[i+2] = chName+'Direction:'+meta[i+2]
            meta[i+3] = chName+'MinimumRawValue:'+meta[i+3]
            meta[i+4] = chName+'MaximumRawValue:'+meta[i+4]
            meta[i+5] = chName+'MinimumPhysValue:'+meta[i+5]
            meta[i+6] = chName+'MaximumPhysValue:'+meta[i+6]
            meta[i+7] = chName+'Resolution:'+meta[i+7]
            meta[i+8] = chName+'PhysicalUnit:'+meta[i+8]
            meta[i+9] = chName+'NumberSpecPoints:'+meta[i+9]
            meta[i+10] = chName+'StartPoint:'+meta[i+10]
            meta[i+11] = chName+'EndPoint:'+meta[i+11]
            meta[i+12] = chName+'Increment:'+meta[i+12]
            meta[i+13] = chName+'AcqTimePerPoint:'+meta[i+13]
            meta[i+14] = chName+'DelayTimePerPoint:'+meta[i+14]
            meta[i+15] = chName+'Feedback:'+meta[i+15]
            meta[i+16] = chName+'Filename:'+meta[i+16]
            meta[i+17] = chName+'DisplayName:'+meta[i+17]
            chlist.append(chName)
            speclist.append(chName)
        elif SpecParameter+'Parameter' in e:
            meta[i] = 'SpecParam:'+ SpecParameter
            meta[i+1] = 'SpecParamRampSpeedEnabled:'+meta[i+1]
            meta[i+2] = 'SpecParamT1us:'+meta[i+2]
            meta[i+3] = 'SpecParamT2us:'+meta[i+3]
            meta[i+4] = 'SpecParamT3us:'+meta[i+4]
            meta[i+5] = 'SpecParamT4us:'+meta[i+5]

    # Split list into pairs
    meta = [e.split(':',1) for e in meta]
    for i in meta:
        if len(i) == 1:
            i.insert(1,'')

    # Create dictionary for metadata
    try:
        meta = {k:v for k,v in meta}
    except:
	logging.error('Metadata extraction error for {}'.format(path))
        meta = dict()

    return meta


def loadPar(meta):
    with open(path) as f:
        meta = f.readlines()
    if not meta:
	logging.info('Empty par file for {}'.format(path))
        return None
    meta = [x.strip('\n') for x in meta]
    return meta


def addComment(meta):
    start = 0
    for i,line in enumerate(meta):
        if line.startswith('Comment'):
            start = i
        if line.startswith('; Scanner Description'):
            end = i
    try:
        comment = ''.join(meta[start:end])
        escape=['?','*','"','.']
        for i in escape:
            comment = comment.replace(i,'')
        comment = comment.replace("'","")
    except:
	logging.info('Comment parsing error for {}'.format(path)) 
        comment = 'Comment:'
    if start != 0:
        for i in range(start,end+1):
            del meta[start]
        meta.insert(start,comment)
    return meta


def fixTimestamp(meta):
    tmp = meta
    # Adjust date as YYYY-MM-DD and time as HH:MM
    try:
        year = '20'+meta['Date'][6:8]
        month = meta['Date'][3:5]
        day = meta['Date'][0:2]
        hours = meta['Date'][8:10]
        seconds = meta['Date'][11:13]
        meta['Time'] = hours+':'+seconds
        meta['Date'] = year+'-'+month+'-'+day
        # Calculate timestamp in seconds
        timeStamp = meta['Date']+'T'+meta['Time']+":00"
        meta['Timestamp'] = timeStamp
    except:
	logging.info('Date parsing error for {}'.format(path))
	meta = tmp
    return meta


def metaHardcoded(path):
    # get metadata hardcoded in path
    year = path.split('/')[4]
    tmp = path.split('/')[5]
    if tmp[:4] != year or path.split('/')[6] == 'FASTSTM':
        continue
    meta = dict()
    fwd = path[:-3] + 'tf0'
    bwd = path[:-3] + 'tb0'
    meta['ImageOriginalName'] = os.path.join(path)
    try:
        meta['ImageHashName'] = str(ImageHash(fwd))
    except FileNotFoundError:
	logging.error('TF0 not found for {}'.format(img))
        try:
            meta['ImageHashName'] = str(ImageHash(bwd))
        except FileNotFoundError:
	    logging.error('TB0 not found for {}'.format(img))
            pass
    return meta


def dateHardcoded(path):
    tmp = path.split('/')[5]
    date = path[:4]+'-'+tmp[4:6]+'-'+tmp[6:]
    return date
