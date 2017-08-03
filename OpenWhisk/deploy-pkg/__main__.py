#import libraries
import numpy as np
import pandas as pd
import re, pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
import email.parser
from bs4 import BeautifulSoup

# email_text_cleaner ( email_text ) - function to cleanse email text
#   parameters:
#     email_text - the entire text of the email
#   returns:
#     clean_text   - the cleansed email subject and body
#     num_of_links - count of links in the email
#
#   example: clean_text, num_of_links = email_text_cleaner ( email_text )
#
def email_text_cleaner ( email_text ):

    # extract subject and body from the email text
    msg = email.message_from_string ( email_text )
    payload = msg.get_payload()
    if type(payload) == type(list()) :
        payload = payload[0] # only use the first part of payload
    sub = msg.get('subject')
    sub = str(sub)
    if type(payload) != type('') :
        payload = str(payload)

    # concat the subject and body
    email_content = sub + payload

    # load the content into beautiful soup to parse the html, if any
    soup = BeautifulSoup(email_content, "lxml")
        
    # Get the number of links-- maybe use to see if email is phishy
    if ( soup.a is not None ):
        num_of_links = len ( soup.a )
    else:
        num_of_links = 0

    # remove script and style elements, may not be necessary for emails
    for script in soup(["script", "style"]):
        script.extract()

    # extract the text
    text = soup.get_text()
        
    # regex to replace non-letters with blank. Note: we also want to remove
    # the phrase "[SPAM]" which is added by some the mailer's spam-detection
    # so we're not cheating :-)
    clean_text = re.sub("\[SPAM\]|[^a-zA-Z]", " ", text ).lower()
    
    return clean_text, num_of_links

# score_email ( email_text ) - function to score email text
#   parameters:
#     email_text - the entire text of the email
#   returns:
#     score  - the probability score that the email is suspicious
#     phishy - 1 for phishy, 0 for not phishy
#
#   example: score, phishy = score_email ( email_text )
#
def score_email ( email_text ):
    
    # unpickle our dictionary and model
    with open ( "dictionary.pkl", "rb" ) as fp:
        dict = pickle.load ( fp )

    model = joblib.load ( 'SpamClassificationModel.pkl' )
    
    # cleanse our email content
    clean_text, num_of_links = email_text_cleaner ( email_text )

    # set up the vectorizer with our dictionary
    vectorizer = CountVectorizer(stop_words='english', vocabulary=dict)
    emailsVec = vectorizer.fit_transform([clean_text])
    
    # if the email contains more than one link, flag it as "phishy"
    phishy = np.sign(num_of_links)
    
    # clean up our features set into a tidy dataframe (note: be sure to preserve the column order!)
    linkDF = pd.DataFrame( {"link_count": [num_of_links], "phishy": [phishy]})
    wordCounts = pd.DataFrame(emailsVec.toarray(), columns=dict) # convert vectors to a dataframe
    emailFeatures = pd.concat([linkDF[["phishy","link_count"]], wordCounts], axis=1) # append the vectors to the labels

    suspicious_score = model.predict_proba ( emailFeatures ) [:,0] [0]
    
    return suspicious_score, phishy

def main(params):
    print(params)
    scores = score_email(params["text"])
    resp = {"score": scores[0].item(), "phishy": scores[1].item()}
    print(resp)
    return resp
