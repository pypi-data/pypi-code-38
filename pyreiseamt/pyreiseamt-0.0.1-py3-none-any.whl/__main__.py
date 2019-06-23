# -*- coding: utf-8 -*-

def main():
    
    # Import Modules
    import pyreiseamt.scraper
    import pyreiseamt.scorer
    import argparse
    import json
    
    # Parse User Input
    parser = argparse.ArgumentParser(description = "Gather country specific information from German Foreign Office")
    parser.add_argument("command", 
                        help = "Command to execute [list or extract]")
    parser.add_argument("-c", "--countries", 
                        help = "Countries to extract seperated by ';'. Extracts all countries if unused.")
    parser.add_argument("-o", "--output", 
                        help = "Where to save extracted information as JSON")
    parser.add_argument("-s", "--sentiment", action = "store_true", 
                        help = "Add sentiment score")
    parser.add_argument("-n", "--nameing", action = "store_true",
                        help = "Use the same name for every top section for every country")
    args = parser.parse_args()
    
    if args.command not in ["list", "extract"]:
        raise ValueError("command should be either 'list' or 'extract'")        # Catch missing command argument
    if args.command == "extract" and args.output is None:
        raise ValueError ("Please specify output")                              # Catch missing output argument if extract command is present
    if args.command == "extract" and not args.output.endswith(".json"):
        raise ValueError("output must end with .json")                          # Catch wrong output format
        
    # Get latest Country Information
    print("Gathering latest data\r", end = "")
    countries = pyreiseamt.scraper.list_countries()                                        # Using internal scraper to get the name and links of all countries
    # React to list command
    if args.command == "list":
        country_names = [x for x in countries]
        country_names.sort()
        format_list = list()
        # Print four countries per line
        i = 0
        total = len(country_names)-1
        while i <= total:
            if total - i >= 4:
                concat_string = " | ".join(country_names[i:i+4])                # If more than four countries are left to print, print all four
            else:
                concat_string = " | ".join(country_names[i:total+1])            # If fewer than four countries are left to print, print all the remaining
            format_list.append(concat_string)
            i += 4
        print("Available Countries: \n")
        print("\n".join(format_list))
        
    # React to extract command
    if args.command == "extract":
        if args.countries is not None:
            countries_to_do = args.countries.split(";")                         # If selection of countries is present, split user input by semicolon
        else:
            countries_to_do = [x for x in countries]                            # Put either all, selected or single country in a list to loop over
        result_extract = list()
        for country in countries_to_do:
            # Get Text
            result_tmp = pyreiseamt.scraper.extract_country(countries[country])            # This command will return the text for the selected country
            # Correct Nameing
            if args.nameing:
                correct_names = ["Country", 
                                 "Landesspezifische Sicherheitshinweise",
                                 "Allgemeine Reiseinformationen",
                                 "Medizinische Hinweise"]                       # Save correct variable names as list
                i = 0
                keys = list(result_tmp.keys())
                for k in keys:                                                  # Since every country has the same variables in the same order,
                    content = result_tmp[k]                                     # we loop through the dictionary, temporarly delete the content
                    del result_tmp[k]                                           # and insert it again under the correct name
                    result_tmp[correct_names[i]] = content
                    i += 1
            # Calculate sentiment for text
            if args.sentiment:
                top_cats = [x for x in result_tmp if x != "Country"]            # Get all top categories except for country name (no sentiment calculation needed)
                top_cat_sentiment = {}                                          # Init dictionary to hold sentiment scores for all top categories
                # Calculate sentiment by top category
                for top_cat in top_cats:                                        # Create a single text variable to hold the text for all sub categories of that top category
                    top_cat_text = ""
                    for sub_cat in result_tmp[top_cat]:
                        top_cat_text = top_cat_text + " " + \
                                       result_tmp[top_cat][sub_cat]
                    top_cat_text = top_cat_text.strip()
                    score = pyreiseamt.scorer.score_text(top_cat_text)                     # Use internal sentiment scorer on top_cat_text for the selected top category
                    top_cat_sentiment[top_cat] = score                          # Add sentiment score for top section to sentiment dictionary
                result_tmp["Sentiment"] = top_cat_sentiment                     # Add sentiment dictionary to result dictionary of country
            result_extract.append(result_tmp)
        # Write final result to JSON
        with open(args.output, mode = "w", encoding = "utf-8") as o:
            json.dump(result_extract, o, ensure_ascii = False, indent = 1)      # Dump dictioanry with entire content to JSON file
        print("Output written to: {}".format(args.output))
        
# Run Main function
if __name__ == "__main__":
    main()                                                                      # Execute code if called in CLI
