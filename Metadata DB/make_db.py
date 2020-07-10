import glob
import argparse
from metadata import *
from database import *

logging.basicConfig(filename='db.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
parser = argparse.ArgumentParser(description='STM meta2db ')
parser.add_argument('--path', '-p', help='path to stm images folder')
parser.add_argument('--table', '-t', help='table of database')

def main():
    args = parser.parse_args()
    path = args.path
    files = glob.glob(os.path.join(path, "**", "*.par"), recursive=True)
    table = args.table
    db_connection, db_cursor = DatabaseConnection()
    try:
        for img in files:
	    meta = metaHardcoded(img)
            par_meta = loadParMeta(img)
            if par_meta != None:
                meta.update(par_meta)
            meta['Date'] = dateHardcoded(img)
            try:
                meta['Timestamp']= date+meta['Timestamp'][10:]
            except:
		logging.info('Timestamp creation error for {}'.format(img))
            try:
                meta2db(meta, table)
            except:
		logging.error('SQL error while uploading metadata for {}'.format(img))
    except Exception as e:
	logging.critical('image {}. Error: {}'.format(img, e))

if __name__ == '__main__':
    main()
