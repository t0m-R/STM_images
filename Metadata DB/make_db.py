import glob
import argparse
import metadata
import database

logging.basicConfig(filename='db.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
parser = argparse.ArgumentParser(description='STM metadata_to_db ')
parser.add_argument('--path', '-p', help='path to stm images folder')
parser.add_argument('--table', '-t', help='table of database')


def main():
    args = parser.parse_args()
    path = args.path
    files = glob.glob(os.path.join(path, "**", "*.par"), recursive=True)
    table = args.table
    for img in files:
        try:
            meta = get_hardcoded_metadata(img)
            par_meta = get_par_metadata(img)
            if par_meta is not None:
                meta.update(par_meta)
            meta['Date'] = get_date(img)
            try:
                meta['Timestamp'] = date + meta['Timestamp'][10:]
            except:
                logging.info('Timestamp creation error for {}'.format(img))
            try:
                metadata_to_db(meta, table)
            except:
                logging.error('SQL error while uploading metadata for {}'.format(img))
        except Exception as e:
            logging.critical('image {}. Error: {}'.format(img, e))


if __name__ == '__main__':
    main()
