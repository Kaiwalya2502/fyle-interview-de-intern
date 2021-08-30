# Your imports go here
import logging
import json
import pandas as pd
import regex as re

logger = logging.getLogger(__name__)

'''
    Given a directory with receipt file and OCR output, this function should extract the amount

    Parameters:
    dirpath (str): directory path containing receipt and ocr output

    Returns:
    float: returns the extracted amount

'''
def extract_amount(dirpath: str) -> float:
    path = dirpath + "/ocr.json" # using only the extracted data from ocr file
    logger.info('extract_amount called for dir %s', dirpath)
    with open(path, encoding = 'utf-8') as f: # loading the file
        data = json.load(f) # json object

    df = pd.json_normalize(data['Blocks'])  # converting json object to flattened dataframe for ease of use all the relevant text recognized
                                            # from the image is stored as part of 'Text' key value pairs, so all text which has a null value
                                            # is dropped from the dataframe in the next step

    df.drop(index = df[df.Text.isna()]['Text'].index,inplace=True)
    receipt_text = " ".join(df.Text.to_list())# the list of Text data is joined as a string to represent text of the receipt
    regex = r"[$]?[ ]*[\d]+([,][\d]+)*[.][\d]{2}"
    # """ regex expression to capture all possible iterations of amount/ money related
    #  values present in the string which is in the format of $(optional){numeric values with or without ','} followed by a decimal
    #  upto 2 decimal places"""

    matches = re.finditer(regex,receipt_text)
    prices_in_receipt = set()
    for match in matches:
        s = str(match.group())
        if '$' in s:
            s = s.replace('$','')       # replacing the symbol $
        if ',' in s:
            s = s.replace(',','')       # removing the commas in the values
        prices_in_receipt.add(float(s)) # converting the values to float and adding to the set to avoid duplicated data

    return max(prices_in_receipt) # returning the max value from the set as amount because of possible sum of items resulting
                                  # in the larger value with the notable exception of discount added after the total amount
                                  # in the receipt which will have to be resolved with the block 'Top' parameter to select
                                  # bottom most value present in the receipt indicating the amount after discount
