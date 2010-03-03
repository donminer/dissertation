class DataSet
   attr_reader :FILENAME, :labels, :vars, :min, :max, :cols

   public

      def initialize(file_name)
         @FILENAME = file_name
         @data = []

         load


      end

      def to_s
         s = ''
         s << '%LABELS ' << labels.join(' ') << "\n"
         s << '%VAR ' << vars.map{|x| DataSet.convert_var(x)}.join(' ') << "\n"
         s << '%MIN ' << min.join(' ') << "\n"
         s << '%MAX ' << max.join(' ') << "\n"
         s << "\n"
         s << @data.map{|row| row.join(' ')}.join("\n")

         s
      end

      def [](idx)
         @data[idx]
      end

      def length
         @data.length
      end

      def each
         @data.each { |row| yield row }
      end

      def each_i
         each_iord(:INDEPENDENT) { |row| yield row }
      end

      def each_d
         each_iord(:DEPENDENT) { |row| yield row }
      end



   private


      def load
         File.open(@FILENAME) do |infile|

            while (raw_line = infile.gets)
               clean_line = DataSet.clean(raw_line)

               # skip over lines with nothing
               if clean_line == '' then next end

               # this is a header line
               if clean_line[0] == '%' then
                  process_header(clean_line)
               else
                  process_datum(clean_line)
               end


            end
         end

      end

      def process_header(line)
         var, items = line.split(/\s/, 2)
         var = DataSet.clean(var)
         items = DataSet.clean(items)

         items = items.split(/\s/)

         if @cols == nil then
            @cols = items.length
         elsif @cols != items.length  then
            throw :bad_num_cols
         end

         case var
            when '%LABELS' then @labels = items
            when '%VAR' then @vars = items.map {|x| DataSet.convert_var(x)}
            when '%MIN' then @min = items.map {|x| x.to_f}
            when '%MAX' then @max = items.map {|x| x.to_f}
         end
      end

      def process_datum(line)
         throw :bad_num_cols unless 
            (newline = line.split(/\s/).map{ |x| x.to_f }).length == @cols

         @data.push(newline)
      end



      def each_iord(i_or_d)
         @data.each do |row|
            new_row = []
            row.zip(@vars).each do |item, var_type|
               if var_type == i_or_d then
                  new_row.push(item)
               end
            end
            yield new_row
         end
      end

      def self.clean(line)
         content, comment = line.split('#')
         content.strip!
         content.squeeze!
         content
      end

      def self.convert_var(item)
         case item
            when 'i' then :INDEPENDENT
            when 'd' then :DEPENDENT
            when :INDEPENDENT then 'i'
            when :DEPENDENT then 'd'
            else throw :bad_var_type
         end
      end



end




x= DataSet.new('fakedata.txt')


 x.each_d {|x| print x, "\n"}
