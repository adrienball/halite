#!/bin/bash

bot_1_wins=0
bot_2_wins=0
bot_3_wins=0
bot_4_wins=0


run_halite() {
    read -ra bot_names <<<$3
    nb_bots=${#bot_names[@]}
    bot_1=${bot_names[0]}
    bot_2=${bot_names[1]}
    if [ ${nb_bots} = 2 ];then
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py"
    elif [ ${nb_bots} = 3 ]; then
        bot_3=${bot_names[2]}
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py" "python3 ${bot_3}.py"
    elif [ ${nb_bots} = 4 ]; then
        bot_3=${bot_names[2]}
        bot_4=${bot_names[3]}
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py" "python3 ${bot_3}.py" "python3 ${bot_4}.py"
    fi
}

is_result_line() {
    line=$1
    read -ra elements <<<${line}
    nb_elements=${#elements[@]}
    if [ ${nb_elements} = 3 ]; then
        return 0
    else
        return 1
    fi
}

process_line() {
    line=$1
    read -ra elements <<<${line}
    bot_id=${elements[0]}
    bot_rank=${elements[1]}
    bot_last_alive=${elements[2]}
    if [ ${bot_rank} = 1 ]; then
        echo ${bot_id}
    fi
}

width=$1
height=$2
iterations=$3

read -ra bot_names <<<$4
nb_bots=${#bot_names[@]}

if [[ ${nb_bots} < 2 || ${nb_bots} > 4 ]]; then
    echo "Invalid number of bots: ${nb_bots}"
fi

for iteration in `seq 1 ${iterations}`
do
    printf "iteration ${iteration}: "
    winner=$(run_halite ${width} ${height} "$4" |
        while IFS= read -r line
        do
            if is_result_line "$line" ; then
                echo $(process_line "$line")
            fi
        done |tr -d '\n')
    printf  "winner is ${winner}\n"

    if [ ${winner} = 1 ]; then
        bot_1_wins=$((${bot_1_wins} + 1))
    elif [ ${winner} = 2 ]; then
        bot_2_wins=$((${bot_2_wins} + 1))
    elif [ ${winner} = 3 ]; then
        bot_3_wins=$((${bot_3_wins} + 1))
    elif [ ${winner} = 4 ]; then
        bot_4_wins=$((${bot_4_wins} + 1))
    fi
done

printf "\n===========RESULTS=============\n"
ratio_1=$((bot_1_wins * 100 / iterations))
printf "\t${bot_names[0]}: ${bot_1_wins} (${ratio_1}%%)\n"
ratio_2=$((bot_2_wins * 100 / iterations))
printf "\t${bot_names[1]}: ${bot_2_wins} (${ratio_2}%%)\n"
if [[ ${nb_bots} > 2 ]]; then
    ratio_3=$((bot_3_wins * 100 / iterations))
    printf "\t${bot_names[2]}: ${bot_3_wins} (${ratio_3}%%)\n"
fi
if [[ ${nb_bots} > 3 ]]; then
    ratio_4=$((bot_4_wins * 100 / iterations))
    printf "\t${bot_names[3]}: ${bot_4_wins} (${ratio_4}%%)\n"
fi
printf "===============================\n"