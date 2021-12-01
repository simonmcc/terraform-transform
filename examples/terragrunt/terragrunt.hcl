terraform {
  before_hook "tftf" {
    commands = ["apply"]
    execute = ["./tftf.sh"]
  }
}
