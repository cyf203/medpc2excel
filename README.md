# medpc2excel

medpc2excel is a Python package for converting single or multiple medpc data files into Excels. 
medpc2excel can also return a pandas DataFrame for further analysis

## Installation

I recommend installing an [Anaconda](https://www.anaconda.com/distribution/) distribution of Python -- Choose Python 3.7 (a higher version like 3.11 causes a problem). 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install medpc2excel. The current version is 3.0.9

```bash
pip install medpc2excel==3.0.9
```

If you downloaded or installed the latest version of Anaconda or Miniconda. You can create a conda environment in your cmd. To do so: 
```bash
conda env create --name <envname> --file=environments.yml
```

If conda has problem to install dependencies, you can also run:
```bash
pip install -r requirements.txt
```

## Version updating note
Add data explorer to visualize timestamp data

## Configure *.MPC file

Please include a medpc protocol file (*.MPC) that you used for behavior task.
The file name of this MPC file should be the same as that of the medpc data file.
The medpc2excel will open the medpc data file and automatically search the used *.MPC file in the same directory.
In *.MPC file, please explicitly declare each array as below:
```text
<... your MPC code...>

    DIM C =9999  \ Levertype                     
    DIM D =9999  \ PelHLON                       
    DIM E =9999  \ PelHLOFF   
    
<... your MPC code ...>
```

## Running medpc2excel

The quickest way to start is to open the GUi from a command line terminal in Anaconda cmd prompt:

```
python -m medpc2excel
```

You can use the data explorer tab to see the raster of each event.
![alt text](https://github.com/cyf203/medpc2excel/blob/master/example/example_fig2.jpg)

You also can import this module and use the function called medpc_read as following
```python
from medpc2excel.medpc_read import medpc_read

f = <file path>

ts_df, log = medpc_read(f, override = True, replace = False) # return a timestamp dataframe and a log string
```

Please download the  ```Example``` folder to your local disk and run the ```medpc2excel_example.py``` to give a try.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. 
Please make sure to update tests as appropriate.

## Dependencies

Pandas==1.3.5\
Numpy==1.21.6\
dill==0.3.7\
mplcursors==0.3\
openpyxl==3.0.5\
matplotlib==3.5.3\
PyQt5==5.11.3\
Medpc2excel==3.0.9
