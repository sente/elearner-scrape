#!/bin/sh


function curl(){
    echo -ne "$(date)\t$@\n" >&2
    command curl -s "$@"
}


function get_initial_data(){

    mkdir GetSchoolStatus
    mkdir GetDegreeStatus
    mkdir GetAllDegreesByCode
    mkdir GetSchoolDegreesByCodeDegreeLevelSubject

    # echo "http://api.elearners.com/directoryws.asmx/GetAllSubjects"
    curl "http://api.elearners.com/directoryws.asmx/GetAllSubjects" > GetAllSubjects.raw

    # echo "http://api.elearners.com/directoryws.asmx/GetAllSchoolsByCode?SourceCode=${SOURCECODE}"
    curl "http://api.elearners.com/directoryws.asmx/GetAllSchoolsByCode?SourceCode=${SOURCECODE}" > GetAllSchoolsByCode.raw

    # echo "http://api.elearners.com/directoryws.asmx/GetAllDegreesByCode?sourcecode=${SOURCECODE}&subject="
    curl "http://api.elearners.com/directoryws.asmx/GetAllDegreesByCode?sourcecode=${SOURCECODE}&subject=" > GetAllDegreesByCode.raw

    # echo "http://api.elearners.com/directoryws.asmx/GetQDFDegreeLevelsByCode?sourcecode=${SOURCECODE}"
    curl "http://api.elearners.com/directoryws.asmx/GetQDFDegreeLevelsByCode?sourcecode=${SOURCECODE}" > GetQDFDegreeLevelsByCode.raw
}

function get_school_degrees_by_degreelevel_subject(){

    grep '<name>' GetQDFDegreeLevelsByCode.raw  | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read DEGREELEVEL;
    do
        DL="${DEGREELEVEL// /+}"
        SUB=""
        # echo "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}"
        curl "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}" > "GetSchoolDegreesByCodeDegreeLevelSubject/degree.subject.${DL}.${SUB}.raw"
    done &

    # echo

    grep '<name>' GetQDFDegreeLevelsByCode.raw  | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read DEGREELEVEL;
    do
        grep '<name>' GetAllSubjects.raw | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read SUBJECT;
        do
            SUB="${SUBJECT// /+}"
            DL="${DEGREELEVEL// /+}"
            # echo "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}"
            curl "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}" > "GetSchoolDegreesByCodeDegreeLevelSubject/degree.subject.${DL}.${SUB}.raw"
        done
    done &

    # echo

    grep '<name>' GetAllSubjects.raw | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read SUBJECT;
    do
        SUB="${SUBJECT// /+}"
        DL=""
        # echo "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}"
        curl "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}" > "GetSchoolDegreesByCodeDegreeLevelSubject/degree.subject.${DL}.${SUB}.raw"
    done &

    # echo

    DL=""
    SUB=""

    # echo "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}"
    curl "http://api.elearners.com/directoryws.asmx/GetSchoolDegreesByCodeDegreeLevelSubject?sourcecode=${SOURCECODE}&degreelevel=${DL}&subject=${SUB}" > "GetSchoolDegreesByCodeDegreeLevelSubject/degree.subject.${DL}.${SUB}.raw"
    
    wait

}

function get_all_subjects(){
    grep '<name>' GetAllSubjects.raw | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read SUBJECT;
    do
        SUB="${SUBJECT// /+}"
        # echo "http://api.elearners.com/directoryws.asmx/GetAllDegreesByCode?sourcecode=${SOURCECODE}&subject=${SUB}"
        curl "http://api.elearners.com/directoryws.asmx/GetAllDegreesByCode?sourcecode=${SOURCECODE}&subject=${SUB}" > "GetAllDegreesByCode/GetAllDegreesByCode.${SUB}.raw"
    done
}

function get_all_schools_by_code(){
    grep '<id>' GetAllSchoolsByCode.raw | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read SCHOOLID;
    do
        # echo "http://api.elearners.com/directoryws.asmx/GetSchoolStatus?sourcecode=${SOURCECODE}&schoolid=${SCHOOLID}";
        curl "http://api.elearners.com/directoryws.asmx/GetSchoolStatus?sourcecode=${SOURCECODE}&schoolid=${SCHOOLID}" > "GetSchoolStatus/GetSchoolStatus.${SCHOOLID}.raw"
    done
}

function get_all_degrees_by_code(){
    grep '<id>' GetAllDegreesByCode.raw | cut -f2 -d'>' | cut -f1 -d'<' | sort -u | while read DEGREEID;
    do
        # echo "http://api.elearners.com/directoryws.asmx/GetDegreeStatus?sourcecode=${SOURCECODE}&degreeId=${DEGREEID}";
        curl "http://api.elearners.com/directoryws.asmx/GetDegreeStatus?sourcecode=${SOURCECODE}&degreeId=${DEGREEID}" > "GetDegreeStatus/GetDegreeStatus.${DEGREEID}.raw"
    done
}


function init() {
    SOURCECODE="$(< apikey.txt )";
    TSTAMP=$(date "+%F_%H.%M.%S")

    mkdir $TSTAMP
    echo $STAMP;

    cd $TSTAMP

    get_initial_data

    get_all_subjects

    get_all_schools_by_code &

    get_all_degrees_by_code &

    get_school_degrees_by_degreelevel_subject &
    
    echo "...waiting"
    wait
    
    echo "...finished"

}

init

#get_initial_data
#get_school_degrees_by_degreelevel_subject
#get_all_subjects
#get_all_schools_by_code
#get_all_degrees_by_code

