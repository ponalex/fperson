import logging.config

LOGGER_CONFIG={
    'version':1,
    'disable_existing_loggers':True,
    'formatters':{
    # add formatters:
    # window_formatter is formatter fo ncurses
        'window_formatter': {
            'format': '%(asctime)s : %(levelname)s [%(module)s  : %(message)s]',
            'datefmt':"%d/%m/%Y %H:%M:%S" 
                },
        # default_formatter is formatter for other
        'default_formatter': {
            'format': '%(asctime)s : %(levelname)s -> %(message)s',
            'datefmt':"%d/%m/%Y %H:%M:%S" 
                },
            },
    'handlers':{
        'stream_handler':{
            'class': 'logging.StreamHandler',
#            'level':'INFO',
            'formatter': 'window_formatter'
                },
        'file_handler':{
            'class': 'logging.FileHandler',
            'mode': "a",
#            'level':'ERROR',
            'filename':'testloger.log',
            'formatter': 'default_formatter'
            }
            },
    'loggers':{
        'curses_logger':{
            'handlers':['file_handler'],
            'level':'WARNING',
            'propagate':True
                },
        'default_logger':{
            'handlers':['file_handler', 'stream_handler'],
            'level':'WARNING',
            'propagate':True
                }
            }
        }

logging.config.dictConfig(LOGGER_CONFIG)

def create_logger(name='default_logger', level=''):
    switcher={
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL,
        '':logging.WARNING
            }

    if name == 'default_logger':
        logger=logging.getLogger(name)
        logger.setLevel(switcher[level])
    else:
        logger=logging.getLogger('curses_logger')
        logger.setLevel(switcher[level])

    return logger
