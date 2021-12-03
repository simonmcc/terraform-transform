terraform {
  before_hook "tf-tf" {
    commands = ["apply"]
    execute = ["./tftf.sh"]
  }
}
