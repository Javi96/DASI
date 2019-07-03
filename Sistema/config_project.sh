source ~/anaconda3/etc/profile.d/conda.sh
conda env create -f env.yml -p ./env
conda init
conda activate ./env
pip install pymongo
pip install pyknow
pip install dialogflow
pip install sklearn
pip install pandas
pip install kmeans
pip install termcolor
sudo apt install mongodb-server-core
sudo apt install mongodb-clients
git clone https://github.com/grei-ufc/pade
cd pade
python setup.py install
cd ..
conda deactivate
echo "end config"