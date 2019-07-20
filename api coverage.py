#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author Ikram
#Description:

table_data = []

def coverapi(orginal_foo):
    '''This trace function which captures the api calls'''
    def inner_evolve_foo(*args, **kwargs):
        import re
        import sys
        import inspect
        import os
        from prettytable import PrettyTable
        from operator import truediv

        WHITE_LIST = ['/lib/python2.7/site-packages/<api path>/apis/','/IntersightDevOpsPythonSDK/<api path>/apis/','/apis/']      
	#specify the api file directory name
        #WHITE_LIST = ['<dir>']
	EXCLUSIONS = ['<']

        def trace(frame, event, arg):

            if event == "call":
                trace.stack_level += 1
                unique_id = frame.f_code.co_filename+str(frame.f_lineno)

                if unique_id in trace.memorized:
                    return

                # Part of filename MUST be in white list.
                if any(x in frame.f_code.co_filename for x in WHITE_LIST) and not any(x in frame.f_code.co_name for x in EXCLUSIONS):

                    if 'self' in frame.f_locals:
                        class_name = frame.f_locals['self'].__class__.__name__
                        func_name = class_name + '.' + frame.f_code.co_name
                    else:
                        func_name = frame.f_code.co_name

                    func_name = '{}'.format(func_name)
                    txt = '{: <40} # {},'.format(func_name, frame.f_code.co_filename)
                    #txt = '{}'.format(frame.f_code.co_filename)
                    #print(txt)
                    filelist = txt.split(',')
                    
                    #getting tabledata
                    getapidata = filter(lambda seq: not re.search(r'(.*init.*)', seq), [line for line in filelist if re.search(r'(.*/apis/)', line)])
                    cleaned = [(i.split('#')[0]).split('.')[0].replace('()', '').strip() for i in getapidata]
                    unq_data = list(set([val for val in cleaned]))
                    table_data.extend(cleaned)
                    #print(txt) #enable this to spitout the trace
                    trace.memorized.add(unique_id)

            elif event == "return":
                trace.stack_level -= 1

        trace.memorized = set()
        trace.stack_level = 0
        sys.setprofile(trace)

        return orginal_foo(*args, **kwargs)

    return inner_evolve_foo


#reading data


def readapi(orginal_foo):
    """Api reader decorator"""

    def wrapper_apireader(*args, **kwargs):
        """Api Wrapper function"""
        import re
        import os
        from prettytable import PrettyTable
        from operator import truediv
        import pymongo

        def apidata():
            """Api reader function"""

            unq_data = list(set(table_data))
            #MongoDB details
            myclient = pymongo.MongoClient('mongodb://10.225.67.149:27017/')
            mydb = myclient['interapidata']
            mycol = mydb['apicollection']
           
            for _id, dbdata in enumerate(unq_data):
            	mycol.insert({"api" : dbdata})
                
            # Deriving table structure from values
            table_fields = PrettyTable()
            table_fields.title = 'INTERSIGHTSDK API COVERAGE SUMMARY/REPORT'
            table_fields.field_names = ['API(S) COVERED IN CURRENT TESTSUITE']
           
            for row in unq_data:
                    table_fields.add_row([row])

            table_fields.add_row([''])
            table_fields.add_row(
                   ['------------------------------------------------------------------------'])
            table_fields.add_row(['PPPercentage of API(S) covered in the TestSuit from IntersightSDK = {:.1%}'.format(
                    truediv(len(unq_data), 274))])
            print(table_fields)

        apidata()

        return orginal_foo(*args, **kwargs)

    return wrapper_apireader
