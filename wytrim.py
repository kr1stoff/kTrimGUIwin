# @CreateTime       : 2022/10/25
# @Author           : mengxf
# @version          : v1.1
# @LastModified     : 2022/10/25
# @description      : 新冠去引物软件 windows 版  

from tkinter import *
from tkinter import ttk, filedialog
from pathlib import Path
import re
import logging
import shutil
import time
import os
from multiprocessing import cpu_count


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class WYTrim():
    """微远去引物软件(专用版)"""
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("微远去引物软件V1.0")
        self.root.geometry("620x650")
        # self.root.iconbitmap(Path(__file__).parent.joinpath('favicon.ico'))
        self.mainframe = ttk.Frame(self.root, padding="10")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def clicked(self):
        # 1.接收fq文件夹路径 2.搜素文件下下面的fq
        dir_fq = filedialog.askdirectory(initialdir=Path(__file__).parent, mustexist=True)
        self.dir_fq = Path(dir_fq).resolve()
        self.pat = re.compile('.(fq|fastq)($|.gz)')
        for _file in Path(dir_fq).iterdir():
            if re.search(self.pat, str(_file)):
                self.lbox.insert('end', str(_file))

    def get_fastq_dir(self):
        """获取fastq文件夹"""
        # 获取fastq文件夹
        self.btn = Button(self.mainframe, text="选择FQ文件夹", bg='#FFFF66', command=self.clicked)
        self.btn.grid(column=0, row=0, sticky=(W, S), padx=5, pady=10)
        # 记录fastq样本的列表,加滚动条
        self.lbox = Listbox(self.mainframe, width=80)
        self.lbox.grid(column=0, row=1, sticky=(N))
        scrbar = ttk.Scrollbar(self.mainframe, orient=VERTICAL, command=self.lbox.yview)
        scrbar.grid(column=1, row=1, sticky=(W, N, S))
        self.lbox['yscrollcommand'] = scrbar.set
        # 增加删除按钮
        self.btn3 = Button(self.mainframe, text='删除项', bg='#FF6666', 
                        command=(lambda x=self.lbox: x.delete(ACTIVE)))
        self.btn3.grid(column=0, row=0, sticky=(E, S), padx=5, pady=10)

    def run_fastp(self, fastq, name):
        """docker运行fastp"""
        cml = f"""
docker run --rm \
    -v {self.dir_fq}:/mnt/docker_volume \
    -w /mnt/docker_volume -i -t \
    kristoffmeng/mambaforge:v1.4 \
    bash -c "fastp --thread {self.threads} -q 15 -u 60 -t 0 -G -n 1 -l 60 -y -a CTGTCTCTTATACACATCTCCGAGCCCACGAGAC \
        --adapter_fasta /wy/adapter.fa -j {name}/{name}.json -h {name}/{name}.html \
        -i {fastq} -o {name}/{name}.clean.1.fq"
        """
        logging.debug(cml)
        os.system(cml)

    def run_ktrim(self, name):
        """docker运行ktrim"""
        cml = f"""
docker run --rm -v {self.dir_fq}:/mnt/docker_volume \
    -w /mnt/docker_volume -i -t \
    kristoffmeng/mambaforge:v1.4 \
    bash -c "python /wy/kTrimPrimer/FQTrimPrimer.py  -w {self.threads} \
        -i {name}/{name}.clean.1.fq \
        -r /wy/NC_045512.2/NC_045512.2.fasta \
        -p /wy/kTrimPrimer/template/SARS-COV-2.FLEX_With_AddonV1V2O_primer_info.tab \
        -o {name}.trimmed.fq"
        """
        logging.debug(cml)
        os.system(cml)
        shutil.move(f'{self.dir_fq}\\ktmp', f'{self.dir_fq}\\{name}')
        shutil.move(f'{self.dir_fq}\\{name}.trimmed.fq.waste.txt', f'{self.dir_fq}\\{name}')
        shutil.move(f'{self.dir_fq}\\{name}.trimmed.fq.primer_stats.tsv', f'{self.dir_fq}\\{name}')

    def run_ktrim_pipe_by_docker(self):
        self.threads = int(cpu_count()/2)
        self.fastqs = self.lbox.get(first=0, last=self.lbox.size())
        for fq in self.fastqs:
            name = re.sub(self.pat, '', Path(fq).name)
            Path(self.dir_fq).joinpath(name).mkdir(parents=True, exist_ok=True)
            self.run_fastp(Path(fq).name, name)
            self.run_ktrim(name)
            realtime = time.strftime("%Y-%m-%d %H:%M:%S ")
            self.text.insert('end', realtime + f'{Path(fq).name} 运行完成!\n')

    def myrun(self):
        """使用docker运行krim流程,包括fastp"""
        self.btn2 = Button(self.mainframe, text='运行', bg='#99CC66', command=self.run_ktrim_pipe_by_docker)
        self.btn2.grid(column=0, row=2, sticky=(W, N, S), padx=5, pady=10)
        self.text = Text(self.mainframe, width=80)
        self.text.grid(column=0, row=3, sticky=(N))
        scrbar2 = ttk.Scrollbar(self.mainframe, orient=VERTICAL, command=self.text.yview)
        scrbar2.grid(column=1, row=3, sticky=(W, N, S))
        self.text['yscrollcommand'] = scrbar2.set

    def execute(self):
        self.get_fastq_dir()
        self.myrun()
        self.root.mainloop()

if __name__ == '__main__':
    wytrim = WYTrim()
    wytrim.execute()
