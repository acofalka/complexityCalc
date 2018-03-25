import argparse
import logging
import complexity_calc

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('program_log.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class ClassNotFoundExc(Exception):
    def __init__(self, message):
        self.message = message


def __import_class(class_name):
    content = class_name.split('.')
    try:
        mod = __import__(content[0])
    except ImportError:
        raise ClassNotFoundExc('Class not found')
    content = content[1:]
    try:
        for c in content:
            mod = getattr(mod, c)
    except AttributeError:
        raise ClassNotFoundExc('Class not found')
    return mod


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('class_name', help='Name of your class', type=str)
    args = parser.parse_args()
    try:
        imported_class = __import_class(args.class_name)
    except ClassNotFoundExc as c:
        logger.exception(c.message)
        print(c.message)
        exit(1)
    logger.debug('Importing class done')
    class_object = imported_class()
    complexity_calc.run(class_object.init_fun, class_object.fun, class_object.cleaner)


if __name__ == '__main__':
    main()




