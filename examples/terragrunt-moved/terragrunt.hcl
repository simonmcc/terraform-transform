terraform {
  before_hook "tf-tf" {
    commands = ["plan"]
    execute = ["./generate-moved.sh"]
  }
}
