#!/bin/bash

run_halite() {
    read -ra bot_names <<<$3
    nb_bots=${#bot_names[@]}
    bot_1=${bot_names[0]}
    bot_2=${bot_names[1]}
    (( nb_bots == 2 )) &&
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py"
    (( nb_bots == 3 )) && bot_3=${bot_names[2]} &&
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py" "python3 ${bot_3}.py"
    (( nb_bots == 4 )) && bot_3=${bot_names[2]} && bot_4=${bot_names[3]} &&
        ./halite -d "$1 $2" -q "python3 ${bot_1}.py" "python3 ${bot_2}.py" "python3 ${bot_3}.py" "python3 ${bot_4}.py"
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
    bot_last_alive=${elements[2]}
    echo "${bot_last_alive};"
}

formatted_result() {
    bot_name=$1
    bot_wins=$2
    iterations=$3
    ratio=$((bot_wins * 100 / iterations))
    echo "${bot_name}: ${bot_wins} (${ratio}%)"
}

bot_1_wins=0
bot_2_wins=0
bot_3_wins=0
bot_4_wins=0

width=$1
height=$2
iterations=$3

read -ra bot_names <<<$4
nb_bots=${#bot_names[@]}

(( nb_bots < 2 || nb_bots > 4 )) && echo "Invalid number of bots: ${nb_bots}" && exit

for iteration in `seq 1 ${iterations}`; do
    printf "iteration ${iteration}: "
    last_alive=$(run_halite ${width} ${height} "$4" |
        while IFS= read -r line; do
            is_result_line "$line" && echo $(process_line "$line")
        done |tr -d '\n')

    last_alive="${last_alive%?}"
    IFS=';' read -ra last_alive_array <<< "$last_alive"

    max_alive=0
    for alive in "${last_alive_array[@]}"; do
        ((alive > max_alive )) && max_alive=${alive}
    done

    IFS=';' read -ra last_alive_array <<< "$last_alive"

    index=1
    for alive in "${last_alive_array[@]}"; do
        if (( alive == max_alive )); then
            (( index == 1 )) && bot_1_wins=$((${bot_1_wins} + 1)) && printf "1 "
            (( index == 2 )) && bot_2_wins=$((${bot_2_wins} + 1)) && printf "2 "
            (( index == 3 )) && bot_3_wins=$((${bot_3_wins} + 1)) && printf "3 "
            (( index == 4 )) && bot_4_wins=$((${bot_4_wins} + 1)) && printf "4 "
        fi
        index=$((${index} + 1))
    done
    printf "\n"
done

printf "\n===========RESULTS=============\n"
echo $(formatted_result ${bot_names[0]} ${bot_1_wins} ${iterations})
echo $(formatted_result ${bot_names[1]} ${bot_2_wins} ${iterations})
(( nb_bots > 2 )) &&
    echo $(formatted_result ${bot_names[2]} ${bot_3_wins} ${iterations})
(( nb_bots > 3 )) &&
    echo $(formatted_result ${bot_names[3]} ${bot_4_wins} ${iterations})
printf "===============================\n"