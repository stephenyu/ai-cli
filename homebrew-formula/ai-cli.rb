class AiCli < Formula
  include Language::Python::Virtualenv

  desc "Convert natural language questions to terminal commands using OpenAI"
  homepage "https://github.com/yourusername/ai-cli"
  url "https://github.com/yourusername/ai-cli/archive/v0.1.0.tar.gz"
  sha256 "YOUR_SHA256_HASH_HERE"
  license "MIT"

  depends_on "python@3.12"

  resource "openai" do
    url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.54.4.tar.gz"
    sha256 "50f3b471085df74c8e54e0af732e67f8723391c8073c50dc2bfa4eddef5b7b5c"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic/pydantic-2.10.3.tar.gz"
    sha256 "cb5ac360ce894ceacd69c403187900a02c4b20b693a9dd1d643e1effab9eadf9"
  end

  resource "keyring" do
    url "https://files.pythonhosted.org/packages/source/k/keyring/keyring-25.5.0.tar.gz"
    sha256 "4c753b3ec91717fe713c4edd522d625889d8973a349b0e582622f49766de58e6"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "AI CLI", shell_output("#{bin}/ai --help")
  end
end 