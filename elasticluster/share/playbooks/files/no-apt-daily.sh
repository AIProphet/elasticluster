#! /bin/sh
#

## defaults

me="$(basename $0)"

# kill 'apt-daily.service' if running
kill='y'

# wait until 'apt-daily.service' job is done
wait='y'

# max time to wait (in seconds) for `apt-get` to terminate
max_wait=300

## usage
usage () {
cat <<EOF
Usage: $me [options]

Ensure that the 'apt-daily.service' systemd job
is not currently running, hence no process *should*
be holding the lock on '/var/apt/lists/lock'.

Options:

  --kill, -k
      Kill any running 'apt-daily.service' job (default).
  --no-kill
      Do not kill 'apt-daily.service' systemd jobs, if any.

  --wait, -w
      Wait until no 'apt-daily.service' job is done (default).
  --no-wait
      Do not wait for 'apt-daily.service' to exit.

  --max-wait NUM
    Wait NUM seconds maximum for 'apt-get' to terminate.
    (Default: $max_wait)

  --help, -h
      Print this help text.

EOF
}


## helper functions

# see /usr/include/sysexit.h
EX_OK=0
EX_USAGE=1
EX_UNAVAILABLE=69
EX_SOFTWARE=70
EX_OSERR=71
EX_TEMPFAIL=75

have_command () {
    command -v "$1" >/dev/null 2>/dev/null
}

die () {
    rc="$1"
    shift
    (echo -n "$me: ERROR: "; if [ $# -gt 0 ]; then echo "$@"; else cat; fi) 1>&2
    exit $rc
}

warn () {
    (echo -n "$me: WARNING: "; if [ $# -gt 0 ]; then echo "$@"; else cat; fi) 1>&2
}

require_command () {
    if ! have_command "$1"; then
        die 1 "Could not find required command '$1' in system PATH. Aborting."
    fi
}

do_or_die () {
    echo "Running command '$@' ..."
    "$@"; rc=$?
    if [ ${rc:-1} -ne 0 ]; then
        die $EX_OSERR "Command '$@' failed. Aborting."
    fi
    return $rc
}

## parse command-line

short_opts='hkw'
long_opts='help,kill,max-wait:,no-kill,no-wait,wait'

# test which `getopt` version is available:
# - GNU `getopt` will generate no output and exit with status 4
# - POSIX `getopt` will output `--` and exit with status 0
getopt -T > /dev/null
rc=$?
if [ "$rc" -eq 4 ]; then
    # GNU getopt
    args=$(getopt --name "$me" --shell sh -l "$long_opts" -o "$short_opts" -- "$@")
    if [ $? -ne 0 ]; then
        die 1 "Type '$me --help' to get usage information."
    fi
    # use 'eval' to remove getopt quoting
    eval set -- $args
else
    # old-style getopt, use compatibility syntax
    args=$(getopt "$short_opts" "$@")
    if [ $? -ne 0 ]; then
        die 1 "Type '$me --help' to get usage information."
    fi
    set -- $args
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        -k|--kill) kill='y' ;;
        --max-wait) max_wait="$2"; shift ;;
        --no-kill) kill='n' ;;
        --no-wait) wait='n' ;;
        -w|--wait) wait='y' ;;
        --) shift; break ;;
    esac
    shift
done


## main

# do nothing if `systemctl` is not available, so we can still use
# the script (to no effect) on older Debian/Ubuntu releases...
if have_command systemctl; then

    # kill 'apt-daily.service' if running
    if [ "$kill" = 'y' ]; then
        systemctl stop apt-daily.service
        systemctl kill --kill-who=all apt-daily.service
    fi

    # wait until `apt-get update` has been killed
    if [ "$wait" = 'y' ]; then
        waited=0
        while [ "$(systemctl show apt-daily.service -p SubState | cut -d= -f2)" != 'dead' ];
        do
            sleep 1
            waited=$(expr 1 + $waited)
            if [ "$waited" -gt "$max_wait" ]; then
                die $EX_TEMPFAIL "Service 'apt-daily' did not terminate within $max_wait seconds."
            fi
        done
    fi

else
    warn "No 'systemctl' command found -- nothing to do."
fi


# exit successfully
exit $EX_OK
