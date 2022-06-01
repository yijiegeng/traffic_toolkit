# traffic_toolkit
## Parameter usage

1. [ -d ] domain name
   * Required!
   * default protocol is https
2. [ -r ] repeat number
   * default number = 1
3. [ -m ] request method
   * candidates: GET, POST, PUT, DELETE, PATCH, OPTIONS
   * default method = GET
4. [ -f ] fast mod
   * use multi-threads to send requests
   * input is thread number
5. [ -a ] attack mod
   * send 13 types of attack requests. Make sure the Syntax Based Detection is enabled on "Known Attack" module of FWB Cloud
   * no need input
   * support [ -f ] mod
6. [ -e ] environment mod
   * send requests through different LB regions in different environments
   * candidates: prod-aws, prod-azure, prod-gcp, dev-aws, dev-azure, dev-gcp, qa2-aws, dev3-aws
   * support [ -f ] mod
7. [ -g ] get_file mod (test for heavy traffic load)
   * receive an empty text file with specific size
   * input is file size (mb)
   * support [ -e ] mod
   * NOT support [ -f ] mod
8. [ -p ] post_file mod (test for heavy traffic load)
   * send and receive two empty text files with specific size
   * input is file size (mb)
   * support [ -e ] mod
   * NOT support [ -f ] mod
