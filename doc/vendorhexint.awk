# Converts mysql hex fileds for  vendorid to device and vendor ints:

# echo "select id, device_id from device" | mysql -u root smolt | sed 's/\:/ /g' | sed 's/0x//g' | awk -f vendorhexint.awk  | sed 's/\=0/=""/g' > mysql
{ 
    printf "update device set vendor_id=%i, device_id=%i where id=%i;\n", $3, $2, $1
}
