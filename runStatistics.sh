#!/bin/bash

bot_1_wins=0
bot_2_wins=0
bot_3_wins=0
bot_4_wins=0


run_halite() {
    read -ra bot_names <<<"$3"
    nb_bots=${#bot_names[@]}
    bot_1=${bot_names[0]}
    bot_2=${bot_names[1]}
    if [ "${nb_bots}" = 2 ];then
        echo "here1"
        echo ${nb_bots}
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py"
    elif [ "${nb_bots}" = 3 ]; then
        bot_3=${bot_names[2]}
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py" "python3 ${bot_3}.py"
    elif [ "${nb_bots}" = 4 ]; then
        bot_4=${bot_names[3]}
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py" "python3 ${bot_3}.py" "python3 ${bot_4}.py"
    else
        echo "Invalid number of bots: ${nb_bots}"
        exit
    fi
}

is_result_line() {
    line=$1
    read -ra elements <<<"${line}"
    nb_elements=${#elements[@]}
    if [ "${nb_elements}" = 3 ]; then
        return 0
    else
        return 1
    fi
}

process_line() {
    line=$1
    read -ra elements <<<"${line}"
    bot_id=${elements[0]}
    bot_rank=${elements[1]}
    bot_last_alive=${elements[2]}
    if [ "${bot_rank}" = "1" ]; then
        echo ${bot_id}
        exit
    else
        echo "0"
    fi
}

width=$1
height=$2
iterations=$3

for iteration in `seq 1 ${iterations}`
do
    printf "\n=======================\n"
    read -ra winner<<<run_halite ${width} ${height} "$4" |
        while IFS= read -r line
        do
            if is_result_line "$line" ; then
                winner_id="$(process_line "$line")"
                if [ "${winner_id}" = "1" ]; then
                    echo 1
                    bot_1_wins=$((${bot_1_wins} + 1))
                elif [ "${winner_id}" = "2" ]; then
                    echo 2
                    bot_2_wins=$((${bot_2_wins} + 1))
                elif [ "${winner_id}" = "3" ]; then
                    echo 3
                    bot_3_wins=$((${bot_3_wins} + 1))
                elif [ "${winner_id}" = "4" ]; then
                    echo 4
                    bot_4_wins=$((${bot_4_wins} + 1))
                else
                    echo 0
                fi
            fi
        done
    printf "winner is ${winner}"
done

#printf "\n===========RESULTS=============\n"
#printf "Wins bot 1: ${bot_1_wins}\n"
#printf "Wins bot 2: ${bot_2_wins}\n"
#printf "Wins bot 3: ${bot_3_wins}\n"
#printf "Wins bot 4: ${bot_4_wins}\n"
#printf "\n===============================\n"
