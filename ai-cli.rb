class AiCli < Formula
  include Language::Python::Virtualenv

  desc "Convert natural language questions to terminal commands using OpenAI"
  homepage "https://github.com/stephenyu/ai-cli"
  url "https://github.com/stephenyu/ai-cli/archive/v0.2.0.tar.gz"
  sha256 "d977fc81708b3eb67dc4e7fa15536772c2a42e08704369f88c8bff8eadb2e24f"  # This will need to be updated with the actual SHA256
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

  resource "pydantic-core" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic-core/pydantic_core-2.27.1.tar.gz"
    sha256 "62a763352879b84aa31058fc931884055fd75089cccbd9d58bb6afd01141b235"
  end

  resource "keyring" do
    url "https://files.pythonhosted.org/packages/source/k/keyring/keyring-25.5.0.tar.gz"
    sha256 "4c753b3ec91717fe713c4edd522d625889d8973a349b0e582622f49766de58e6"
  end

  resource "jaraco-classes" do
    url "https://files.pythonhosted.org/packages/source/j/jaraco-classes/jaraco_classes-3.4.0.tar.gz"
    sha256 "47a024b51d0239c0dd8c8540c6c7f484be3b8fcf0b2d85c13825780d3b3f3acd"
  end

  resource "jaraco-functools" do
    url "https://files.pythonhosted.org/packages/source/j/jaraco-functools/jaraco_functools-4.1.0.tar.gz"
    sha256 "70f7e0e2ae076498e212562325e805204fc092d7b4c17e0e86c959e249701a9d"
  end

  resource "more-itertools" do
    url "https://files.pythonhosted.org/packages/source/m/more-itertools/more_itertools-10.5.0.tar.gz"
    sha256 "5482bfef7d1a8398504944af4402d4ac05b686a90bddb8e0c5b35d4f8cbc3c36"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test that the package was installed correctly
    assert_match "0.2.0", shell_output("#{bin}/ai --version 2>&1")
    
    # Test that help command works
    help_output = shell_output("#{bin}/ai --help")
    assert_match "Convert natural language questions to terminal commands", help_output
  end
end 
