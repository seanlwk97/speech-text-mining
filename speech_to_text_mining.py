# Author: Sean Leong Wei Kok

idx = 1

while True:
    print('------------------------------------------START--------------------------------------------------')

    import time

    start = time.time()

    import speech_recognition as sr
    import re
    import nltk
    from nltk.tokenize import sent_tokenize
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    import punctuator
    import os
    import pandas as pd
    import json
    nltk.download('wordnet')
    from nltk.corpus import wordnet
    nltk.download('stopwords')
    from textblob import TextBlob

    import pyrebase


    import ast
    import itertools
    from collections import Counter

    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import db

    # nltk.download('punkt')

    from datetime import date
    from datetime import datetime


    # In[2]:


    today = date.today()
    print("Today's date:", today)

    today = str(today).replace('-','_')

    print("Today's date:", today)


    # ## Setup

    # In[3]:


    INPUT_FOLDER_NAME = 'INPUT'
    PUNCTUATED_FOLDER_NAME = 'OUTPUT'


    ROOT_DIR = os.getcwd()
    INPUT_FOLDER = os.path.join(ROOT_DIR,INPUT_FOLDER_NAME)
    PUNCTUATED_FOLDER = os.path.join(ROOT_DIR,PUNCTUATED_FOLDER_NAME)

    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)

    if not os.path.exists(PUNCTUATED_FOLDER):
        os.makedirs(PUNCTUATED_FOLDER)


    # ## Download data from Firebase

    # In[4]:


    FIREBASE_FOLDER_NAME = "FIREBASE_STORAGE_RECORDS"

    FIREBASE_FOLDER =os.path.join(ROOT_DIR,FIREBASE_FOLDER_NAME)

    if not os.path.exists(FIREBASE_FOLDER):
        os.makedirs(FIREBASE_FOLDER)


    # cred = credentials.Certificate("FIREBASE_STORAGE_RECORDS/studentplanner-1712e-firebase-adminsdk-j4w7q-b1ff384c50.json")
    # firebase_admin.initialize_app(cred)

    config= {
      "apiKey": "AIzaSyA-neHuZcqrBlCFXVqk7kppz9FmRivxtMY",
      "authDomain": "studentplanner-1712e.firebaseapp.com",
      "databaseURL": "https://studentplanner-1712e.firebaseio.com",
      "projectId": "studentplanner-1712e",
      "storageBucket": "studentplanner-1712e.appspot.com",
      "messagingSenderId": "447714992182",
      "appId": "1:447714992182:web:876ddd230913e1482b7897",
      "serviceAccount": "FIREBASE_STORAGE_RECORDS/studentplanner-1712e-firebase-adminsdk-j4w7q-b1ff384c50.json"
    }

    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()


    datadir = 'Audio_Recorder/'

    all_files = storage.child("Audio_Recorder").list_files()



    permission = 0

    for  file in all_files:

        file_str = str(file)
        file_list = file_str.split(",")

        wanted_file = file_list[1].strip()

    #     print('wanted file = {}'.format(wanted_file))

        real_wanted_file = wanted_file.split('/')[0].strip()

    #     print('real_wanted_file = {}'.format(real_wanted_file))

        if real_wanted_file == "Audio_Recorder":


            permission = 1
            real_wanted_file_name = wanted_file.split('/')[1].strip()

            print('real_wanted_file_name = {}'.format(real_wanted_file_name))

            firebase = pyrebase.initialize_app(config)
            storage = firebase.storage()

            path_on_cloud = 'Audio_Recorder/{}'.format(real_wanted_file_name)
            path_local = 'FIREBASE_STORAGE_RECORDS/{}.wav'.format(real_wanted_file_name)

            print('path_on_cloud = {}'.format(path_on_cloud))
            print('path_local = {}'.format(path_local))

            storage.child(path_on_cloud).download(path_local)

            print("AUDIO FILE DOWNLOADED!")

        else:
            print("NO AUDIO FILE, QUIT LOOPING")
            break


        print('\n')

        # ## Speech to Text Conversion

        # In[5]:
    print("permission is {}".format(permission))
    if permission == 1:

        print("---------------------------------AUDIO FILE DETECTED, PROCESSING!----------------------------------")
        AUDIO_FILE = path_local

        print("AUDIO FILE = {}".format(AUDIO_FILE))
        # AUDIO_FILE = ("speech2_FEMALE.wav")
        # AUDIO_FILE = ("speech3_INDIAN.wav")


        r = sr.Recognizer()

        with sr.AudioFile(AUDIO_FILE) as source:
            #reads the audio file. Here we use record instead of
            #listen
            audio = r.record(source)

        total_text = r.recognize_google(audio)
        # total_text = sample_recognize(AUDIO_FILE)



        print(type(total_text))

        print('\n')

        with open("{}\SAMPLE_1.txt".format(INPUT_FOLDER_NAME), "w") as text_file:
            text_file.write(total_text)


        # !cat INPUT\SAMPLE_1.txt | python punctuator.py INTERSPEECH-T-BRNN.pcl OUTPUT\OUTPUT_1.txt
        get_ipython().system('cat INPUT\\SAMPLE_1.txt | python punctuator.py Demo-Europarl-EN.pcl OUTPUT\\OUTPUT_1.txt')


        def listToString(s):

            # initialize an empty string
            str1 = " "

            # return string
            return (str1.join(s))


        def plural_to_singular(keyword):

            text_blob_object = TextBlob(keyword)

            text_list = text_blob_object.words.singularize()

            new_keyword = listToString(text_list)

            return new_keyword


        # DICTIONARY INPUT fUNCTION

        def final_dict_function(dictionary_name, input_lvl_1_word, input_lvl_2_word, INFORMATION):

            for level_1_keyword in dictionary_name.copy():
                #         print('level_1_keyword : {}'.format(level_1_keyword))

                if level_1_keyword == input_lvl_1_word:

                    for level_2_keyword in dictionary_name[level_1_keyword]:

                        #                 print('level_2_keyword : {}'.format(level_2_keyword))

                        if level_2_keyword == input_lvl_2_word:
                            dictionary_name[level_1_keyword][level_2_keyword] = INFORMATION

            return dictionary_name


        def find_synonym_list(word):

            synonyms = []

            for syn in wordnet.synsets(word):
                for l in syn.lemmas():
                    synonyms.append(l.name())

            return list(set(synonyms))


        # ## Information Processing

        # In[5]:

        important_keywords_level_1_ori = ['assignment', 'coursework', 'homework', 'tutorial', 'lab', 'exam', 'test']
        important_keywords_level_2_ori = ['title', 'objective', 'objectives', 'deadline', 'submission', 'requirement']

        target_word_list_1 = []
        target_word_list_2 = []
        target_word_dict_level_1 = {}
        wanted_word_L1_list = []
        wanted_word_L2_list = []
        essence_list = []
        final_essence_list = []

        important_keywords_level_1 = []
        important_keywords_level_2 = []

        essence_list = []

        stop_words = set(stopwords.words("english"))

        with open("{}\OUTPUT_1.txt".format(PUNCTUATED_FOLDER_NAME), "r") as read_file:
            punctuated_text = read_file.read()
        #     print(punctuated_text)

        new_punctuated_text = punctuated_text.replace('COMMA', '').replace('PERIOD', '').replace('COLON', '')
        new_punctuated_text_list = sent_tokenize(new_punctuated_text)
        # print(new_punctuated_text_list)

        total_word_list = word_tokenize(new_punctuated_text)

        for word in important_keywords_level_1_ori:
            similar_word_list = find_synonym_list(word)

            important_keywords_level_1.append(word)
            important_keywords_level_1.extend(similar_word_list)

        for word in important_keywords_level_2_ori:
            similar_word_list = find_synonym_list(word)

            important_keywords_level_2.append(word)
            important_keywords_level_2.extend(similar_word_list)

        print(important_keywords_level_1)

        print('\n')
        print(important_keywords_level_2)

        for word in total_word_list:
            if word in important_keywords_level_1:
                target_word_list_1.append(word)

            if word in important_keywords_level_2:
                target_word_list_2.append(word)

        print('\n')

        for sentence in new_punctuated_text_list:

            sentence_list = word_tokenize(sentence)
            remove_word_list = []

            essence_list = []

            for word in sentence_list:

                if word in target_word_list_1:
                    print('word = {}'.format(word))

                    remove_word_list.append(word)

                    wanted_word_L1_list.append(word)

                if word in target_word_list_2:
                    remove_word_list.append(word)
                    wanted_word_L2_list.append(word)

            TARGET_1 = any(elem in important_keywords_level_1 for elem in remove_word_list)
            TARGET_2 = any(elem in important_keywords_level_2 for elem in remove_word_list)

            CONDITION = TARGET_1 or TARGET_2

            if CONDITION == True:

                for index, remove_word in enumerate(remove_word_list):

                    if index == 0:
                        print('remove_word = {}'.format(remove_word))
                        important_information = sentence.replace(remove_word, '')

                    else:
                        print('remove_word = {}'.format(remove_word))
                        important_information = important_information.replace(remove_word, '')

                tokens = word_tokenize(important_information)
                result = [i for i in tokens if not i in stop_words]
                seperator = ' '
                new_important_information = seperator.join(result)

                #         remove_word_str = ' '.join([str(elem) for elem in remove_word_list])

                #         new_essence_for_dict =  str(remove_word_list)  + '+'+ new_important_information
                #         essence_list = new_essence_for_dict.split('+')

                essence_list.append(remove_word_list)
                essence_list.append(new_important_information)

                final_essence_list.append(essence_list)

                print('remove_word_list ={}'.format(remove_word_list))
                print('original sentence = {}'.format(sentence))
                print('important_information ={}'.format(important_information))
                print('new important_information ={}'.format(new_important_information))
                print('\n')
                #         print('new_essence_for_dict={}'.format(new_essence_for_dict))
                print('essence list = {}'.format(essence_list))

                # print(type(new_important_information))

            print('\n')
            print('---------next sentence ------------')
            print('\n')

        print(final_essence_list)

        print('\n')

        old_wanted_word_L2_list = wanted_word_L2_list

        text_blob_object_1 = TextBlob(listToString(wanted_word_L1_list))
        text_blob_object_2 = TextBlob(listToString(wanted_word_L2_list))

        wanted_word_L1_list = text_blob_object_1.words.singularize()
        wanted_word_L2_list = text_blob_object_2.words.singularize()

        print('WANTED_WORD_L1_LIST = {}'.format(wanted_word_L1_list))
        print('WANTED_WORD_L2_LIST = {}'.format(wanted_word_L2_list))
        print('OLD_WANTED_WORD_L2_LIST = {}'.format(old_wanted_word_L2_list))

        # In[6]:

        new_wanted_word_L1_list = []

        print('wanted_word_L1_list = {}'.format(wanted_word_L1_list))
        print('\n')

        for item in wanted_word_L1_list:

            index = 1
            print("current item is: {}".format(item))

            if item in new_wanted_word_L1_list:
                while item in new_wanted_word_L1_list:
                    index += 1
                    temp_item = item.split('_')
                    item = temp_item[0]
                    item = '{}_{}'.format(item, index)

                new_wanted_word_L1_list.append(item)
            else:
                new_wanted_word_L1_list.append(item)

        print('\n')

        print('new_wanted_word_L1_list = {}'.format(new_wanted_word_L1_list))

        # ## Organization of Information

        # In[7]:

        # wanted_word_L1_list = list(dict.fromkeys(wanted_word_L1_list))
        wanted_word_L2_list = list(dict.fromkeys(wanted_word_L2_list))

        print('wanted_word_L1_list: {}'.format(wanted_word_L1_list))
        print('wanted_word_L2_list: {}'.format(wanted_word_L2_list))

        wanted_word_L2_dict = dict.fromkeys(wanted_word_L2_list)
        print(wanted_word_L2_dict)

        print('---------------------------------------------------------------------------------------------------')

        # Dictionary Creation
        for key in new_wanted_word_L1_list:

            if key in target_word_dict_level_1:

                print('key = {}'.format(key))
            #         if key == 'assignment':

            #             target_word_dict_level_1[key]

            else:
                target_word_dict_level_1[key] = wanted_word_L2_dict

        print('\n')

        target_word_dict_level_1_str = str(target_word_dict_level_1)
        final_dict_str = target_word_dict_level_1_str.replace('[', '{').replace(']', '}')

        # final_dict = json.loads(final_dict_str)
        final_dict = ast.literal_eval(final_dict_str)

        # print(final_dict)
        # print(type(final_dict))

        print('---------------------------------------------------------------------------------------------------')

        temp_lvl_1_list = []

        # Input to Dictionary

        for item_level_1 in final_essence_list:
            #     print(item_level_1)

            index = 1

            obtained_keyword = item_level_1[0]
            INFORMATION = item_level_1[1]

            level_1_keyword_set = set(wanted_word_L1_list).intersection(obtained_keyword)
            level_2_keyword_set = set(old_wanted_word_L2_list).intersection(obtained_keyword)

            level_1_keyword = repr(level_1_keyword_set)
            level_2_keyword = repr(level_2_keyword_set)

            TARGET_3 = any(elem in wanted_word_L1_list for elem in obtained_keyword)
            TARGET_4 = any(elem in old_wanted_word_L2_list for elem in obtained_keyword)

            index = 1

            if TARGET_3 == False:
                level_1_keyword_stripped = None

            else:

                level_1_keyword_stripped = level_1_keyword[2:-2]

                level_1_keyword_stripped = plural_to_singular(level_1_keyword_stripped)

                if level_1_keyword_stripped in temp_lvl_1_list:
                    while level_1_keyword_stripped in temp_lvl_1_list:
                        index += 1
                        temp_item = level_1_keyword_stripped.split('_')
                        level_1_keyword_stripped = temp_item[0]
                        level_1_keyword_stripped = '{}_{}'.format(level_1_keyword_stripped, index)

                        previous_lvl_1 = level_1_keyword_stripped

                    temp_lvl_1_list.append(level_1_keyword_stripped)

                else:
                    temp_lvl_1_list.append(level_1_keyword_stripped)

                    previous_lvl_1 = level_1_keyword_stripped

            if TARGET_4 == False:
                level_2_keyword_stripped = None

            else:
                level_2_keyword_stripped = level_2_keyword[2:-2]

                level_2_keyword_stripped = plural_to_singular(level_2_keyword_stripped)

            print('level_1_keyword_ = {}'.format(level_1_keyword))
            print('level_2_keyword_ = {}'.format(level_2_keyword))

            print('level_1_keyword_stripped = {}'.format(level_1_keyword_stripped))
            print('level_2_keyword_stripped = {}'.format(level_2_keyword_stripped))
            print('INFORMATION = {}'.format(INFORMATION))

            #     TARGET_3 = any(elem in wanted_word_L1_list for elem in obtained_keyword)

            #     if TARGET_3 == True:
            #     if level_1_keyword_stripped in temp_dict:
            #         temp_dict[level_1_keyword_stripped]+=1
            #     else:
            #         temp_dict[level_1_keyword_stripped]=1

            #     print(temp_dict)
            #     print(INFORMATION)

            #      for key in temp_dict.copy():
            #             dict_num =

            if level_1_keyword_stripped == None:

                #         final_dict_new = final_dict_function(final_dict, previous_lvl_1, level_2_keyword_stripped, INFORMATION)

                if previous_lvl_1 == None:

                    continue


                else:

                    final_dict_new = final_dict_function(final_dict, previous_lvl_1, level_2_keyword_stripped,
                                                         INFORMATION)


            else:

                final_dict_new = final_dict_function(final_dict, level_1_keyword_stripped, level_2_keyword_stripped,
                                                     INFORMATION)

            print('\n')
            print('----------next item--------------')
            print('\n')

        print(final_dict_new)


        print("\n")
        


        import json
        import collections

        JSON_FILE_NAME = 'TESTING.json'

        od = collections.OrderedDict(sorted(final_dict_new.items()))

        with open(JSON_FILE_NAME,'w') as g:
            json.dump(od,g)


        print("DONE!")


        # ## Upload processed data into Firebase

        # In[ ]:


        from firebase import firebase

        firebase = firebase.FirebaseApplication('https://studentplanner-1712e.firebaseio.com', None)
        new_user = 'Lecture_{}'.format(idx)

        idx += 1

        destination_path = '/Module/{}/Assessments'.format(real_wanted_file_name)

        result = firebase.put(destination_path,new_user, final_dict_new)
        print(result)
        print("REALTIME DATABASE UPDATED!!!")




        # ## Remove audio file from local/Firebase storage

        # In[ ]:


        if os.path.exists(path_local):
            os.remove(path_local)   #remove local storage

            print("Local Audio File Deleted!")


        storage.delete(path_on_cloud)     #remove Firebase storage

        print("Firebase Audio File Deleted!")



        print('elapsed_time={}'.format(time.time()- start))

    else:
        print("--------------------------FINDING AUDIO FILE-------------------------")


    permission = 0

