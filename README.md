# medpc2excel

medpc2excel is a Python package for convert single or multiple medpc data file into Excels. 
medpc2excel can also return a pandas DataFrame for further analysis

## Installation

I recommend installing an [Anaconda] (https://www.anaconda.com/distribution/) distribution of Python -- Choose Python 3.7. 

Use the package manager [pip] (https://pip.pypa.io/en/stable/) to install medpc2excel. Current version is 1.4.1

```bash
pip install medpc2excel
```

To upgrade medpc2excel (package here), run the following in the environment:
```bash
pip install medpc2excel --upgrade
```

## Configure *.MPC file

Please include a medpc protocol file (*.MPC) that you used for behavior task.
The file name of this MPC file should be the same as in the medpc data file.
The medpc2excel will open the medpc data file and automatically search the used *.MPC file in the same directory.
In *.MPC file, please explicitly declare each array as below:
```text
    DIM C =9999  \ Levertype                     
    DIM D =9999  \ PelHLON                       
    DIM E =9999  \ PelHLOFF                      
```

## Use medpc2excel

```python
from medpc2excel import medpc_read

f = <file path>
rat_id = 2

medpc_read(f, rat_id, replace = False) # return a m2e object
medpc_read.date  #return the experiment data in the current data file
medpc_read.subj_list #return a list contains all subject ID
medpc_read.get_subj_df (rat_id) #return a dataframe contains all timestamp arrays for rat #2
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. 
Please make sure to update tests as appropriate

## Dependencies 

OS\
Pandas\
Numpy\
re

