#!/bin/zsh

RUNDIR='/home/slymane/vlslice/vlslice'
cd $RUNDIR

# launch tmux session and start flask server
tmux new-session -d -s vlslice 'source ~/anaconda3/etc/profile.d/conda.sh; conda activate vlslice; python server/server.py'
tmux split-window

# Start autobuilding Svelte client
tmux send "cd $RUNDIR/client; npm run autobuild" ENTER
tmux a
