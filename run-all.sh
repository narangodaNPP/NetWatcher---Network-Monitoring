cd server
export FLASK_APP=server.py ; flask run --host 0.0.0.0 --port 5001

cd workers
sudo python3 worker.py &

cd ../monitors
./run-monitors-all.sh &

cd ../ui
npm start &