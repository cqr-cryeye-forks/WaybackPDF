#!/usr/bin/env python3
# coding: utf-8

import json
import requests
import argparse


class PC:
    """PC (Print Color)
    Used to generate some colorful, relevant, nicely formatted status messages.
    """
    green = '\033[92m'
    blue = '\033[94m'
    orange = '\033[93m'
    endc = '\033[0m'
    ok_box = blue + '[*] ' + endc
    note_box = green + '[+] ' + endc
    warn_box = orange + '[!] ' + endc


def parse_arguments():
    desc = ('OSINT tool to download archived PDF files from archive.org for'
            ' a given website.')
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-d', '--domain', type=str, action='store',
                        required=True,
                        help='The target domain you are looking for files')
    parser.add_argument('-o', '--output', type=str, action='store',
                        required=False,
                        help='Optional output directory (Default is the domain name)')
    parser.add_argument('--http', type=str, action='store',
                        required=False,
                        help='Use HTTP instead of HTTPS for the target domain.'
                             ' The default behavior uses HTTPS')
    parser.add_argument('-r', '--resume', type=int, action='store', required=False,
                        help='Start downloading at a given index and skip X previous'
                             ' files')

    args = parser.parse_args()
    return args


def getPDFlist(domain, protocol):
    print("\n" + PC.ok_box + "Requesting PDF list...")

    # Default target is HTTPS
    targetDomain = "https://{}".format(domain)

    # Building URL
    if protocol:
        targetDomain = "http://{}".format(domain)

    baseURL = "https://web.archive.org/web/timemap/"
    payload = {'url': targetDomain,
               'matchType': 'prefix',
               'collapse': 'urlkey',
               'output': 'json',
               'fl': 'original,mimetype,timestamp,endtimestamp,groupcount,uniqcount',
               'filter': '!statuscode:[45]..',
               'limit': '100000',
               '_': '1587473968806'}

    # HTTP request to get PDF list

    try:
        raw = requests.get(baseURL, params=payload).json()
    except requests.exceptions.RequestException as e:
        print("\n" + PC.warn_box + f"Exiting! Error connecting to the Wayback server: {e}")
        return []

    # Building the PDF list
    files = []
    headers = raw[0]

    for item in raw[1:]:
        file = {}
        for i, header in enumerate(headers):
            file[headers[i]] = item[i]
        files.append(file)

    pdfs = []
    result_final = []
    for file in files:
        if file['mimetype'] == 'application/pdf':
            pdfs.append(file)

    if pdfs:
        for pdf in pdfs:
            # Create direct URL for each PDF
            pdf_path = 'https://web.archive.org/web/' + pdf['timestamp'] + 'if_/' + pdf['original']
            result_final.append({"pdffile": pdf_path})

        print("\n" + PC.note_box + f"Writing Results done: {result_final}")
        return result_final

    else:
        print("\n" + PC.warn_box + f"No PDF files found!")
        return []


def write_data_to_file(result_final, output):
    print("\n" + PC.ok_box + "Writing Result to file...")
    print("\n" + PC.ok_box + f"Result to write: {result_final}")

    with open(output, "w") as output_file:
        json.dump(result_final, output_file, indent=2)


def main():
    """Main Function"""
    args = parse_arguments()
    outputFile = args.output

    print("\n" + PC.note_box + "Web Archive PDF Downloader ")
    print(PC.note_box + "Target domain : " + args.domain)
    print(PC.note_box + f"Output file : {outputFile}")

    # Getting the PDF list
    result_final = getPDFlist(args.domain, args.http)

    # Downloading PDF
    write_data_to_file(result_final, outputFile)

    print("\n" + PC.ok_box + "Everything's done !")


if __name__ == "__main__":
    main()
