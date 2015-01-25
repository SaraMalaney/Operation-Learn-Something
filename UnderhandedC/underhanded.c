#include <stdio.h>
int main()
{
	printf("Hello World\n");
	return 0;
}

typedef struct user_struct {
        int user_id;
        time_t when_created;
        time_t last_activity;
        char * name;
        char * URL_of_avatar;

        int num_following, * ids_following;
        int num_blocked, * ids_blocked;
} user;

typedef struct piu_struct {
        int piu_id;
        int piu_id_of_repiu, user_id_of_repiu;    /* zero if not a re-Piu */

        int user_id_of_poster;
        user * poster;              

        char piu_text_utf8[140*4+1];
        unsigned char piu_length;   /* UTF8 characters, not bytes */
        unsigned char visible_only_to_followers;
} piu;

typedef struct surveillance_request_struct {
        int id_number;
        int num_patterns;
        user * user_patterns;
        piu * piu_patterns;
        FILE * write_here;
} surveillance_request;

int num_requests;
surveillance_request * requests_to_scan;

void surveil( piu * entry ){

	for (request in requests_to_scan){
		if ((entry contains request.piu_patterns)&&(entry.poster.ids_following == request.user_patters.id_number)
	}
}
The Piu text in the pattern is a substring of the input Piu’s text; AND
All ids_following and ids_blocked in the user pattern are followed/blocked by the input Piu’s user; AND
All of the NONZERO fields in the piu pattern match the input Piu. Values set to zero are “don’t care” inputs.