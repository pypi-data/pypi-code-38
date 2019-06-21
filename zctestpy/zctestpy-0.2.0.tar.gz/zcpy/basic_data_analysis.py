from __future__ import print_function
import os
import re
import sys


def trim_adaptors(fastq_dir, strain_barcode_dict, barcode_kits='EXP-NBD104', outdir='', thread=16, demultiplexing=False):
    """
    Trim adaptors and demultiplexing using guppy_barcoder and qcat
    """
    try:
        with open(os.path.join(outdir, '1.demultiplexing_trimming.sh'), 'w') as f:
            flag = 0
            if os.path.isdir(fastq_dir):
                for item in os.listdir(fastq_dir):
                    if item.endswith('.fastq.gz') or item.endswith('.fastq') or item.endswith('.fq.gz') or item.endswith('.fq'):
                        flag = 1
                        break
                if flag == 0:
                    print('Error: Not found ".fastq(.gz)" or ".fq(.gz)" format files in dir {}.'.format(fastq_dir))
                    sys.exit(-1)
        
            if demultiplexing is False:
                for key in strain_barcode_dict.keys():
                    tmp_path = os.path.join(outdir, 'tmp.fastq')
                    prefix = os.path.join(outdir, 'trimmed_{}'.format(strain_barcode_dict[key][1]))
                    f.write('cat {} >{} | qcat --trim --detect-middle -f {} -o {}.fastq\nrm {}\n'.format(os.path.join(fastq_dir, '*.fastq'), tmp_path, tmp_path, prefix, tmp_path))
                # f.write('cat {} >{} | qcat --trim --detect-middle -f {} -o {}/trimmed_sample.fastq\nrm {}\n'.format(os.path.join(fastq_dir, '*.fastq'), os.path.join(outdir, 'tmp.fastq'), outdir, os.path.join(outdir, 'tmp.fastq'), os.path.join(outdir, 'tmp.fastq')))

            else:
                f.write('guppy_barcoder -i {} --barcode_kits {} -s {}/barcode_demultiplexing_data --min_score 80 -q 100000000 -t {}\n'.format(fastq_dir, barcode_kits, outdir, thread))

                if barcode_kits == 'EXP-NBD103' or barcode_kits == 'EXP-NBD104':
                    barcode_kits_qcat = 'NBD103/NBD104'
                elif barcode_kits == 'EXP-NBD114':
                    barcode_kits_qcat = 'NBD114'
                else:
                    barcode_kits_qcat = 'NBD104/NBD114'

                for key in strain_barcode_dict.keys():
                    print('qcat -k {} --trim --detect-middle -f {}/barcode_demultiplexing_data/{}/*.fastq -o {}/barcode_demultiplexing_data/trimmed_{}.fastq\n'.format(barcode_kits_qcat, outdir, key, outdir, strain_barcode_dict[key][1]))
                    f.write('qcat -k {} --trim --detect-middle -f {}/barcode_demultiplexing_data/{}/*.fastq -o {}/barcode_demultiplexing_data/trimmed_{}.fastq\n'.format(barcode_kits_qcat, outdir, key, outdir, strain_barcode_dict[key][1]))

        print('####### Demultiplexing Using Guppy and Trimming Adaptors Using Qcat ########')
        os.system('sh {}/1.demultiplexing_trimming.sh'.format(outdir))
    except Exception as e:
        raise e


def quality_control_pauvre(outdir='', prefix=None):
    """
    Quality control using pauvre
    """
    try:
        with open(os.path.join(outdir, '3.quality_control_pauvre.sh'), 'w') as f:
            if os.path.isdir('{}/barcode_demultiplexing_data'.format(outdir)):
                if not os.path.exists(os.path.join(outdir, 'quality_control')):
                    os.makedirs(os.path.join(outdir, 'quality_control'))
                for item in os.listdir('{}/barcode_demultiplexing_data'.format(outdir)):
                    if item.endswith('.fastq.gz') or item.endswith('.fastq') or item.endswith('.fq.gz') or item.endswith('.fq'):
                        prefix = re.sub('.fastq.gz|.fastq|.fq.gz|.fq|.gz', '', os.path.basename(item))
                        tmp_name = '{} read length vs mean quality'.format(prefix)
                        f.write('pauvre marginplot -f {}/barcode_demultiplexing_data/{} -y -t \"{}\" -o {}_QCstat >{}/quality_control/{}_QCstat.out && mv *.png {}/quality_control\n'.format(outdir, item, tmp_name, prefix, outdir, prefix, outdir))
            else:
               for item in os.listdir(outdir):
                    if item.startswith('trimmed_') and (item.endswith('.fastq.gz') or item.endswith('.fastq') or item.endswith('.fq.gz') or item.endswith('.fq')):
                        prefix = re.sub('.fastq.gz|.fastq|.fq.gz|.fq|.gz', '', os.path.basename(item))
                        tmp_name = '{} read length vs mean quality'.format(prefix)
                        f.write('pauvre marginplot -f {}/{} -y -t \"{}\" -o QCstat >{}/QCstat.out && mv *.png {}\n'.format(outdir, item, tmp_name, outdir, outdir))                
                    elif item.startswith('filtered_') and (item.endswith('.fastq.gz') or item.endswith('.fastq') or item.endswith('.fq.gz') or item.endswith('.fq')):
                        prefix = re.sub('.fastq.gz|.fastq|.fq.gz|.fq|.gz', '', os.path.basename(item))
                        tmp_name = '{} read length vs mean quality'.format(prefix)
                        f.write('pauvre marginplot -f {}/{} -y -t \"{}\" -o filtered_QCstat >{}/filtered_QCstat.out && mv *.png {}\n'.format(outdir, item, tmp_name, outdir, outdir))                

                # f.write('pauvre marginplot -f {}/trimmed_sample.fastq -y -o QCstat >{}/QCstat.out && mv *.png {}\n'.format(outdir, outdir, outdir))
                # f.write('pauvre marginplot -f {}/filtered_trimmed_sample.fastq -y -o filtered_QCstat >{}/filtered_QCstat.out && mv *.png {}\n'.format(outdir, outdir, outdir))

        print('####### Quality Control Using Pauvre ########')
        os.system('sh {}/3.quality_control_pauvre.sh'.format(outdir))
    except Exception as e:
        raise e


def filter_reads(outdir='', min_quality=7, min_length=500, max_length=10000000):
    try:
        with open(os.path.join(outdir, '2.filter_reads.sh'), 'w') as f:
            if os.path.isdir('{}/barcode_demultiplexing_data'.format(outdir)):
                for item in os.listdir('{}/barcode_demultiplexing_data'.format(outdir)):
                    prefix = os.path.join(outdir, 'barcode_demultiplexing_data', 'filtered_{}'.format(item))
                    if item.endswith('.fastq.gz') or item.endswith('.fq.gz'):
                        f.write('gunzip -c {}/barcode_demultiplexing_data/{} | NanoFilt -q {} -l {} --maxlength {} |gzip > {}\n'.format(outdir, item, min_quality, min_length, max_length, prefix))
                    elif item.endswith('.fastq') or item.endswith('.fq'):
                        f.write('cat {}/barcode_demultiplexing_data/{} | NanoFilt -q {} -l {} --maxlength {} |gzip > {}.gz\n'.format(outdir, item, min_quality, min_length, max_length, prefix))
            else:
                for item in os.listdir(outdir):
                    prefix = os.path.join(outdir, 'filtered_{}'.format(item))
                    if item.endswith('.fastq.gz') or item.endswith('.fq.gz'):
                        f.write('gunzip -c {}/{} | NanoFilt -q {} -l {} --maxlength {} |gzip > {}\n'.format(outdir, item, min_quality, min_length, max_length, prefix))
                    elif item.endswith('.fastq') or item.endswith('.fq'):
                        f.write('cat {}/{} | NanoFilt -q {} -l {} --maxlength {} |gzip > {}.gz\n'.format(outdir, item, min_quality, min_length, max_length, prefix))
                # f.write('cat {}/trimmed_sample.fastq | NanoFilt -q {} -l {} --maxlength {} > {}/filtered_trimmed_sample.fastq\n'.format(outdir, min_quality, min_length, max_length, outdir, outdir))

        print('####### Filter Low Quality and Short Reads Using NanoFilt ########')
        os.system('sh {}/2.filter_reads.sh'.format(outdir))
    except Exception as e:
        raise e


def basic_data_analysis(input, strain_barcode_dict, outdir=None, flowcell='FLO-MIN106', kit='SQK-LSK109', barcode_kits='EXP-NBD104', thread=16, barcoding=False, min_quality=7, min_length=500, max_length=1000000000):
    if outdir is None or outdir == '':
        outdir = '.' 
    else:
        outdir = outdir
        if outdir.endswith('/'):
            outdir = re.sub('/$', '', outdir)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

    trim_adaptors(fastq_dir=input, strain_barcode_dict=strain_barcode_dict, barcode_kits=barcode_kits, outdir=outdir, thread=thread, demultiplexing=barcoding)

    filter_reads(outdir, min_quality, min_length, max_length)
    quality_control_pauvre(outdir)
