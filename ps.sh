# Purpose: shortcut for showing `ps` info along with current date.
# Run with: ./ps.sh
ps aux; ps -eo pid,lstart,cmd; echo Now: $(date)

